import sys
import app.engine.user_model
from app.db.db_procs import SQLRequest

sys.path.insert(0, "/")
import helpers
import click
from flask import Flask
from flask_login import (
    LoginManager
)


application = Flask(__name__, template_folder="/app/app/templates")
application = helpers.create_app(application)


# initialize DB at first run via "flask init_db" command
@application.cli.command("init_db")
def init_db():
    return SQLRequest().init_db()


# import after app is created
from app.blueprints.page import page
from app.blueprints.user import user

application.register_blueprint(page)
application.register_blueprint(user)

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(application)


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return app.engine.user_model.User(user_id).get()

