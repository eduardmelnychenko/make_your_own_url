#!/usr/bin/python3
import sys
sys.path.insert(0, "./app/")
from helpers import create_app
from app_run import application

application = create_app(application)

