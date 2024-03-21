# This file create an image for our application by taking a base distro linux image (alpine)
# that have python already install on it.

FROM python:3.12

RUN pip install poetry==1.8.2

WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN poetry install
COPY src ./src
RUN poetry install

ENTRYPOINT ["poetry", "run", "python", "-m", "uvicorn", "src.main:app"]
