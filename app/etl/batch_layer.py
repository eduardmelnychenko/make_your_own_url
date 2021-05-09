#  This module is for storing master dataset and computing views

import redis
import logging
import ast
from app.creds.settings import CacheSettings
from app.db.db_procs import SQLRequest
redis_client = redis.Redis(host=CacheSettings.REDIS_HOST,
                           port=CacheSettings.REDIS_PORT,
                           password=CacheSettings.REDIS_PASS)
# from celery import Celery


def run_batch():
    data_rows = []
    click_log = redis_client.lpop(CacheSettings.CLICK_LOGS)

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
        batch_res = SQLRequest().execute_values(query=query, data_values=data_rows)
        logging.info(f"Success: {batch_res}, n_clicks: {len(data_rows)}")
    else:
        logging.info("No clicks were logged this time")
