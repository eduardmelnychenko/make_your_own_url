# Make your own url web app
Deploy and host your own url shortener and link management system in a few minutes.
It's an open-source SaaS application built with Python/Dash/Flask/Bootstrap4/PostgreSQL/Redis/nginx/Docker/OAuth.
The docker image comes with preset Postgres/Redis instances, but you can easily switch to external ones for better scalability/performance.

## Prerequisites:
1. Registered domain.
2. GCP Developer account.
3. Cloud/local instance with accessible IP with Docker installed. 
4. Logo in SVG (optional).

## Features
* Url customization
* Click analytics IN PROCESS
* Link management TODO
* Users administration TODO

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
5. On the first run you will need to initialize the database with the following commands:
   * connect to the app container shell: ``sudo docker exec -it your_own_url /bin/bash`` 
   * run flask cli command in the shell: ``flask init_db``
   * if you see ``DB is initialized successfully`` then everything is good
     
## Security & settings
* .database.env for DB credentials and settings
* .redis.env for Redis credentials and settings
* Redis and Postgres hosts are set in `app/creds/settings.py` in corresponding classes