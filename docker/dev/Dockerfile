FROM python:3.8.13-slim-bullseye

# set work directory
WORKDIR /usr/src/app

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY requirements.txt .
RUN apt-get -y update \
    && apt-get --no-install-recommends -y install make gcc g++ subversion musl-dev libpq-dev\
    && pip install --upgrade pip wheel \
    && pip install --no-cache-dir -r requirements.txt

COPY docker/dev/entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

COPY prism/. .

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]