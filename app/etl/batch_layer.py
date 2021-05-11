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
    # writes logs to db
    sender.add_periodic_task(CelerySettings.UPDATE_LOGS_TIMEOUT, batch_write_to_db.s(),
                             name='celery_tasks.batch_write_to_db')

    # updates mat.views
    sender.add_periodic_task(CelerySettings.UPDATE_VIEWS_TIMEOUT, update_mat_views.s(),
                             name='celery_tasks.update_mat_views')


@CELERY.task(name="celery_tasks.batch_write_to_db")
def batch_write_to_db(message="Start batch_write_to_db") -> None:
    data_rows = []
    click_log = redis_client.lpop(CacheSettings.CLICK_LOGS)
    logging.info(message)
    while click_log:
        decoded_click_log = ast.literal_eval(click_log.decode())
        logging.debug(decoded_click_log)
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


@CELERY.task(name="celery_tasks.update_mat_views")
def update_mat_views(message="Start update_mat_views") -> None:
    logging.info(message)

    mat_views = ["user_url_cnt_view", "user_daily_cnt_view", "url_info_view"]
    with application.app_context():
        for mat_view in mat_views:
            res = SQLRequest().execute_query(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {mat_view}")
            if res is True:
                logging.info(f"Successfully updated: {mat_view}")
            else:
                logging.info(f"Failed to update: {mat_view}")
    logging.info("Finished mat.views refresh")


@CELERY.task(name="celery_tasks.delete_urls")
def delete_urls(urls_ids, customer_id):

    with application.app_context():
        res0 = SQLRequest().execute_query(f"DELETE FROM URLS WHERE suffix IN ({urls_ids}) and user_id='{customer_id}'")
        res1 = SQLRequest().execute_query(f"REFRESH MATERIALIZED VIEW CONCURRENTLY url_info_view")
        if all([res0, res1]) is True:
            logging.info(f"Successfully deleted: {urls_ids}")
        else:
            logging.info(f"Failed to delete: {urls_ids}")
