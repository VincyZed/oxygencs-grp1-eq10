FROM python:3.12.3-alpine as builder

WORKDIR /code
 
COPY ./requirements.txt /code/requirements.txt
RUN \
 apk add --no-cache python3 postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc python3-dev musl-dev postgresql-dev && \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps

COPY ./src /code/src

WORKDIR /code/src
CMD [ "pipenv", "run", "start" ]
