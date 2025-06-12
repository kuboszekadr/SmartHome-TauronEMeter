FROM python:3.12-bullseye

COPY . /app
WORKDIR /app

RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.in-project true