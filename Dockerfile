## To implement
FROM python:3.12.3-alpine as builder

WORKDIR /code

RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    postgresql-dev \
    && apk add --no-cache --virtual .build-deps \
    build-base

COPY Pipfile Pipfile.lock /code/

RUN  pip install pipenv && \ 
    pipenv install

COPY . /code/
RUN apk del .build-deps
EXPOSE 80

CMD ["pipenv", "run", "start"]