FROM python:3.11-slim-buster
WORKDIR /app

ENV POETRY_VERSION=1.3.2

RUN pip install poetry==$POETRY_VERSION

COPY poetry.lock pyproject.toml /app/

RUN poetry export --format requirements.txt > requirements.txt
RUN pip3 install -r requirements.txt

COPY . /app

CMD [ "waitress-serve", "--call", "main:create_app"]
