# Make your own url web app
You can deploy and host your own url shortener and link management system in a few minutes.
It's an open-source application built with Python/Dash/Flask/Bootstrap4/PostgreSQL/nginx/Docker.

## Prerequisites:
1. Registered domain.
2. GCP Developer account.
3. Cloud/local instance with accessible IP with Docker installed. 
4. Logo in SVG (optional).

## Features
* TODO

## Installation instructions
1. Register your app with GCP console and get credentials. 
   The app does not provide 
   its own password management, instead it employs Google OAuth process.
2. Rename file settings_sample.py to settings.py and enter your own credentials.
3. If you want to try/test it on local machine, run `sudo  docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build`.
   Make sure you added ``localhost`` to app credentials in GCP
4. If you want to deploy it on host, you have 2 options:
   * Use existing nginx server (e.g., you share the instance with other web services). Run ``sudo docker-compose -f docker-compose.yml -f docker-compose.host.yml up --build``
   Configure nginx to route your domain name and set up your https certificate (Letsencrypt is a good free choice).
   * Use preset docker image with nginx/Letsencrypt. You need just set your domain in `nginx-prod.yml` and then run
    ``sudo docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build``
