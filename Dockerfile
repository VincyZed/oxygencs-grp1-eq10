FROM python:3.12.3-alpine

# Set the working directory to /code
WORKDIR /code

# Copy Pipfile to /code
COPY Pipfile /code/

# Copy Pipfile.lock to /code
COPY Pipfile.lock /code/

# Install dependencies
RUN apk add --no-cache python3 postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc python3-dev musl-dev postgresql-dev && \
    python3 -m pip install pipenv && \
    pipenv install --deploy && \
    apk --purge del .build-deps

# Copy the rest of the application code
COPY ./src /code/src

# Set the entrypoint to use pipenv
ENTRYPOINT ["pipenv", "run"]
CMD ["start"]
