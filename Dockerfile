FROM python:3.7-slim

LABEL maintainer="eduard@recommendme.online"

RUN apt-get update
RUN apt-get -y install build-essential python-dev

RUN mkdir /app/
ADD requirements.txt /app/

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app/
RUN pip install -r requirements.txt
COPY ./ /app/

RUN useradd --home-dir=/app --uid=1000 uwsgi_user
RUN mkdir /data
RUN chmod -R 777 /data

USER uwsgi_user

CMD uwsgi --strict uwsgi.ini