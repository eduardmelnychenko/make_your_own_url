import psycopg2.extras as pg_extras
import psycopg2 as pg
from flask import g, current_app
from app.db.redis_instance import redis_client


def get_db():
    print('Connecting DB')
    g.db = pg.connect(
        dbname=current_app.config['DB_NAME'],
        user=current_app.config['USERNAME'],
        host=current_app.config['HOST'],
        port=current_app.config['DB_PORT'],
        password=current_app.config['PASSWORD'],
        cursor_factory=pg_extras.DictCursor)
    return g.db


class SQLRequest:

    def __init__(self):
        self.db = get_db()

    @staticmethod
    def close_db():
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def init_db(self):
        conn = self.db
        cursor = conn.cursor()
        try:
            cursor.execute(open("schema.sql", "r").read())
            self.db.commit()
            print("DB is initialized successfully")
            res = True
        except Exception as error:
            print("Cannot initialize DB: ", error)
            res = False
        finally:
            if cursor:
                cursor.close()
            if self.db:
                self.db.close()
        return res

    def execute_query(self, query):
        conn = self.db
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            self.db.commit()
            res = True
        except Exception as error:
            print("Exception is: ", error)
            res = False
        finally:
            if cursor:
                cursor.close()
            if self.db:
                self.db.close()
        return res

    def get_data(self, query):
        res = None
        cursor = self.db.cursor()
        try:
            cursor.execute(query)
            res = cursor.fetchall()
            print(res)
        except Exception as error:
            print("Exception is: ", error)
        finally:
            if cursor:
                cursor.close()
            if self.db:
                self.db.close()
        return res


def save_url(short_suffix, long_uri, user_id=None, date_expire=None):
    # push to redis
    n_days_to_live = 30 * 86400  # 30 days in seconds
    redis_client.set(name=short_suffix, value=long_uri, ex=n_days_to_live)

    # save to DB
    if user_id:
        if date_expire:
            save_query = f"INSERT INTO urls (suffix, long_url, user_id, date_expire)" \
                         f" VALUES ('{short_suffix}', '{long_uri}', '{user_id}', {date_expire})"
        else:
            save_query = f"INSERT INTO urls (suffix, long_url, user_id)" \
                         f" VALUES ('{short_suffix}', '{long_uri}', '{user_id}')"
    else:
        save_query = f"INSERT INTO urls (suffix, long_url)" \
                     f" VALUES ('{short_suffix}', '{long_uri}')"

    res = SQLRequest().execute_query(save_query)

    return res


def check_for_url(short_suffix: str) -> str:
    long_url = redis_client.get(short_suffix)
    if not long_url:
        req = f"SELECT long_url FROM urls WHERE suffix='{short_suffix}'"
        res = SQLRequest().get_data(req)
        if len(res) > 0:
            return res[0][0]
        else:
            return '404'
    return long_url


def log_click(suffix, click_source):
    log_q = f"INSERT into click_log (suffix_id) VALUES ('{suffix}')"

    if click_source:
        loq_q = f"INSERT into click_log (suffix_id, click_source) VALUES ('{suffix}', '{click_source}')"

    res = SQLRequest().execute_query(log_q)

    return res


def basic_table_compose(headers, q_string) -> dict:
    """
    creates dict for a basic table
    """
    print(q_string)
    data = SQLRequest().get_data(q_string)

    return {"headers": headers, "data": data}
