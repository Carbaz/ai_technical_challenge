FROM python:3.13-slim AS base
RUN groupadd -r rungroup && useradd -rm runuser -g rungroup
WORKDIR /service
ENV PIPENV_DONT_LOAD_ENV=1
RUN apt-get update && apt-get install -y --no-install-recommends wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade --no-cache-dir pip wheel pipenv
COPY Pipfile ./
COPY Pipfile.lock ./
RUN chown -R runuser:rungroup .
USER runuser
RUN pipenv install --deploy --clear
HEALTHCHECK --start-period=15s --interval=10s --timeout=5s --retries=3 \
    CMD wget localhost:${GRADIO_HTTP_PORT:-7860}/ --spider || exit 1

FROM base AS init
WORKDIR /service
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        tesseract-ocr \
        poppler-utils && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
COPY /app ./app
COPY /tools ./tools
COPY /policies ./policies
RUN chown -R runuser:rungroup .
USER runuser
ENTRYPOINT ["tools/initialize.sh"]

FROM base AS development
WORKDIR /service
USER runuser
RUN pipenv install --deploy --clear --dev
ENTRYPOINT ["pipenv", "run", "python", "-Bm", "app"]

FROM base AS production
WORKDIR /service
USER root
COPY /app ./app
COPY /tools ./tools
RUN chown -R runuser:rungroup .
USER runuser
ENTRYPOINT ["pipenv", "run", "python", "-Bm", "app"]

FROM production AS testing
WORKDIR /service
USER root
COPY setup.cfg ./
COPY pytest.ini ./
COPY /tests ./tests
RUN chown -R runuser:rungroup .
USER runuser
RUN pipenv install --deploy --clear --dev
ENTRYPOINT ["tail", "-f", "/dev/null"]
