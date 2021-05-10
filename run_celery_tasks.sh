#!/bin/bash
celery -A app.etl.batch_layer worker --loglevel=INFO