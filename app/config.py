import logging
from os import environ, urandom
from app.creds import settings


class Config(settings.GoogleSecrets, settings.DbSecrets, settings.CacheSettings, settings.CelerySettings):
    DEBUG = False
    TESTING = False
    SECRET_KEY = environ.get("APP_SECRET_KEY", default=urandom(16))


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = 'INSECURE_FOR_LOCAL_DEVELOPMENT'

    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
