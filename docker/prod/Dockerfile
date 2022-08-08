###########
# BUILDER #
###########

FROM python:3.8.13-slim-bullseye as builder

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY requirements.txt .
RUN apt-get -y update \
    && apt-get --no-install-recommends -y install make gcc g++ subversion musl-dev libpq-dev\
    && pip install --upgrade wheel \
    && pip wheel --wheel-dir=/root/wheels -r requirements.txt


#########
# FINAL #
#########

# pull official base image
FROM python:3.8.13-slim-bullseye

# create directory for the app user
RUN mkdir -p /home/prism

# create the app user
RUN groupadd --gid 2000 prism \
    && useradd --uid 2000 --gid prism --shell /bin/bash --create-home prism

# create the appropriate directories
ENV HOME=/home/prism
ENV APP_HOME=/home/prism/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
RUN mkdir $APP_HOME/mediafiles
WORKDIR $APP_HOME

# install dependencies
RUN apt-get -y update && apt-get --no-install-recommends -y install libpq-dev
COPY --from=builder /root/wheels /root/wheels
COPY ./requirements.txt .
RUN pip install --no-index --find-links=/root/wheels -r ./requirements.txt

# copy project
COPY prism/. $APP_HOME

COPY docker/prod/entrypoint.sh .
RUN sed -i 's/\r$//g' $APP_HOME/entrypoint.sh
RUN chmod +x $APP_HOME/entrypoint.sh

# chown all the files to the app user
RUN chown -R prism:prism $APP_HOME

# change to the app user
USER prism

ENTRYPOINT [ "/home/prism/web/entrypoint.sh" ]