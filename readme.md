# Algemene Rekenkamer Utility and Auth Server

## Linting

```bash
flake8 src main.py seed.py
```

## Testing

````bash
pytest --cov


# Algemene Rekenkamer Utility Server

## Description

This is a utility server that contains the business logic for interacting with Elastic. Its used by dashboards like [this](https://github.com/bingneef/rekenkamer-search). It is written in Python and uses Flask.

## Getting started

```bash
cp example.env .env # and fill in the correct values
poetry install --no-root
poetry run python3 main.py
```

This start a development server on port 5000. It automatically reloads on file changes.

## Deployment

GH actions (or similar) is not yet properly implemented. Thus make sure to run the command below before create a new docker image

```bash
flake8 src main.py seed.py
pytest --cov
```

You can create a new docker image by running the following command:

```bash
./build-and-deploy.sh <tag>
```

When tag is empty, it defaults to `latest`.
````
