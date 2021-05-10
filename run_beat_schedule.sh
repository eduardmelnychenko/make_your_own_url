#!/bin/bash
celery -A app.etl.batch_layer beat -s /tmp/celerybeat-schedule --loglevel=INFO
