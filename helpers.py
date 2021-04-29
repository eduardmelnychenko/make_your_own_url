from os import environ
from app.config import DevelopmentConfig, ProductionConfig


def create_app(app_obj):

    environment = environ.get("FLASK_ENV", default="development")
    cfg = DevelopmentConfig()

    if environment == "production":
        cfg = ProductionConfig()

    app_obj.config.from_object(cfg)
    app_obj.secret_key = cfg.SECRET_KEY

    return app_obj
