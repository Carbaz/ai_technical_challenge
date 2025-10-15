FROM python:3.13-slim AS base
RUN groupadd -r rungroup
RUN useradd -rm runuser -g rungroup
WORKDIR /service
ENV PIPENV_DONT_LOAD_ENV=1
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg2 \
    ca-certificates && \
    wget https://developer.download.nvidia.com/compute/cuda/repos/debian11/x86_64/cuda-keyring_1.0-1_all.deb && \
    dpkg -i cuda-keyring_1.0-1_all.deb && \
    apt-get update && \
    apt-get install -y --no-install-recommends cuda-cudart-12-0 && \
    rm -rf /var/lib/apt/lists/* cuda-keyring_1.0-1_all.deb
RUN pip install --upgrade --no-cache-dir pip wheel pipenv
COPY Pipfile ./
COPY Pipfile.lock ./
RUN chown -R runuser:rungroup .
USER runuser
RUN pipenv install --deploy --clear
HEALTHCHECK --interval=10s --start-period=15s --retries=3 --timeout=5s \
    CMD wget localhost:${GRADIO_HTTP_PORT:-7860}/ --spider || exit 1

FROM base AS init
WORKDIR /service
USER root
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
