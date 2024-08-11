FROM python:3.12.4-slim-bullseye

RUN pip install poetry

COPY . /app

WORKDIR /app

RUN poetry install

CMD [ "poetry", "run","python", "main.py" ]