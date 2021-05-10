#  This module is for storing master dataset and computing views

import redis
import logging
import ast
from app.creds.settings import CacheSettings, CelerySettings
from app.db.db_procs import SQLRequest
from app_run import application

from celery import Celery
# from celery.schedules import crontab

CELERY = Celery('celery_tasks',
                backend=CelerySettings.CELERY_BACKEND_URL,
                broker=CelerySettings.CELERY_BROKER_URL)

redis_client = redis.Redis(host=CacheSettings.REDIS_HOST,
                           port=CacheSettings.REDIS_PORT,
                           password=CacheSettings.REDIS_PASS)


@CELERY.on_after_configure.connect
def batch_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0, run_batch.s(), name='celery_tasks.run_batch_click_log')


@CELERY.task(name="celery_tasks.run_batch_click_log")
def run_batch(message="Start run_batch"):
    data_rows = []
    click_log = redis_client.lpop(CacheSettings.CLICK_LOGS)
    print(message)
    while click_log:
        decoded_click_log = ast.literal_eval(click_log.decode())
        print(decoded_click_log)
        data_rows.append(decoded_click_log)
        click_log = redis_client.lpop(CacheSettings.CLICK_LOGS)

    if len(data_rows) > 0:
        query = f"INSERT INTO click_log " \
                f"(suffix_id, int_ip_address, platform, browser, version, lang, ip, country_code, country_name," \
                f"region_code, region_name, city, zip_code, time_zone, latitude, longitude) " \
                f"VALUES %s ON CONFLICT DO NOTHING"
        with application.app_context():
            batch_res = SQLRequest().execute_values(query=query, data_values=data_rows)
        logging.info(f"Success: {batch_res}, n_clicks: {len(data_rows)}")
    else:
        logging.info("No clicks were logged this time")
