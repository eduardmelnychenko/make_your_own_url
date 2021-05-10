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
RUN chmod +x run_celery_tasks.sh
RUN chmod +x run_beat_schedule.sh

USER uwsgi_user

CMD uwsgi --strict uwsgi.ini
