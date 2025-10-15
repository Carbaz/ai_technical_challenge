# Prompt to generate the README documentation

Write a professional README.md documentation for this project.

The project is a technical challenge described in CHALLENGE.md.

You must use **all the files included in the project**, not only code files but also:

* Project configuration files.
* Dockerfiles.
* Docker Compose files.
* Any other relevant documentation or metadata.

At the end of the README, include a list of all the files you used as reference to
generate the documentation.

The README must include all standard sections, such as:

* Project overview and purpose.
* Architecture and folder structure.
* Getting started: cloning, installing dependencies, and running the project.
* Main dependencies with brief explanations.
* Strategic decisions and motivations.
* Tools available in the `tools/` folder and their usage.

Include a dedicated **Usage Guide** section with:

* Step-by-step instructions for running the application in different scenarios:

  * Running locally using the ChromaDB container from the `dockers/` folder.
  * Running in development mode using `docker-compose`, which mounts the source code.
  * Running in production mode using `docker-compose-prod`, which copies the code into
    the image.

* Configuration options and how to modify them.
* Notes on Docker Compose profiles and the `init` container, which is only used when
  rebuilding the database.
* Placeholder references for screenshots using the format:

  `![Screenshot: <description>](path/to/screenshot.png)`

Do not generate or embed actual images. Just leave clear references where screenshots
should be added.

Markdown formatting rules (mandatory):

* No line should exceed 89 characters.
* Use asterisks (*) for unordered list bullets.
* Headings must be surrounded by blank lines.
* Lists must be surrounded by blank lines.
* Do not truncate or mutilate text to fit the line limit — use multiline formatting
  when necessary.
* All code blocks must explicitly specify the language (e.g., ` ```bash`, ` ```python`).
  If unsure about the language, use ` ```txt` as a fallback.

Content rules (mandatory):

* Do not invent or assume any functionality, configuration, or usage that is not
  present in the actual project.
* Do not add optional features, alternatives, or speculative enhancements unless they
  are already implemented.

At the end of the README, include a separate section titled **Limitations and Future
Improvements**, where you may describe:

* Known limitations or current shortcomings of the project.
* Potential improvements, refactors, or features that could be added in the future.

This section must appear only at the end of the document.
