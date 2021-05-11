from app.db.db_procs import SQLRequest, check_for_url
from app.db.redis_instance import redis_client
from app.engine.user_model import User
import uuid
from random import randint
from urllib.parse import urlparse
from app.creds.settings import BlockedUrls, OwnUrls

from flask import request


class SuffixAlreadyExists(Exception):
    """Raised when short url suffix already exists"""
    pass


class Url:
    """
    Url class defines structure and methods for creating, updating, and verifying short and long urls.
    """

    def __init__(self, suffix=None, current_user=User('-999')):
        self.suffix = suffix
        self.current_user = current_user
        self.already_exists = self.if_suffix_exists()
        self.long_url, self.short_url, self.description, self.date_added, self.date_expire = self.get_url_data()

    def if_suffix_exists(self) -> bool:

        if self.suffix in OwnUrls.COMMON_SUFFIXES.union(OwnUrls.USER_SUFFIXES):
            return True

        res = False
        if self.suffix:
            long_url = redis_client.get(self.suffix)
            if not long_url:
                query = f"select exists(select 1 from urls where suffix='{self.suffix}')"
                res = SQLRequest().get_data(query)[0][0]

        return res

    def get_url_data(self) -> list:
        res = (None,) * 5
        if self.suffix and self.already_exists is True:
            query = f"SELECT long_url, short_url, description, date_added::TEXT, date_expire::TEXT" \
                    f" FROM urls where suffix='{self.suffix}'"
            res = SQLRequest().get_data(query)[0]
        return res

    def print_info(self) -> None:
        print(f"suffix: {self.suffix}, original url: {self.long_url},"
              f" short url: {self.short_url}, user_id: {self.current_user.id}, days to live: {self.date_expire}, "
              f" already exists: {self.already_exists} ")

    def create_url(self, long_url, description='', days_to_live=None) -> bool:

        res = False

        if Url().verify_url(long_url):
            self.long_url = long_url

            self.description = description

            self.short_url, self.suffix = self.generate_full_short_urls(custom_suffix=self.suffix)

            if self.suffix:

                if days_to_live:

                    expiry_date = f"CURRENT_DATE + INTERVAL '{days_to_live} days'"

                    save_query = f"INSERT INTO urls (suffix, long_url, short_url, description, user_id, date_expire)" \
                                 f" VALUES ('{self.suffix}','{self.long_url}','{self.short_url}', " \
                                 f"'{self.description}', '{self.current_user.id}', {expiry_date})"
                else:
                    save_query = f"INSERT INTO urls (suffix, long_url, short_url, description, user_id)" \
                                 f" VALUES ('{self.suffix}', '{self.long_url}','{self.short_url}'," \
                                 f"'{self.description}'," \
                                 f"'{self.current_user.id}')"

                res = SQLRequest().execute_query(save_query)

        if res is True:
            # push to redis
            n_days_to_live = 30 * 86400  # 30 days in seconds
            redis_client.set(name=self.suffix, value=self.long_url, ex=n_days_to_live)

        return res

    def update_url(self, long_url, description=None, manual_date_expire=None) -> bool:
        update_columns = f"long_url='{long_url}'"
        if description:
            update_columns = update_columns + ", " + f"description='{description}'"
        if manual_date_expire:
            update_columns = update_columns + ", " + f"date_expire='{manual_date_expire}'"
        update_query = f"UPDATE urls SET {update_columns} WHERE suffix='{self.suffix}'"

        res = SQLRequest().execute_query(update_query)

        return res

    def delete_url(self) -> bool:
        if self.suffix:
            return SQLRequest().execute_query(f"delete from urls where suffix='{self.suffix}'")
        return False

    @staticmethod
    def get_host_url() -> str:
        o = urlparse(request.base_url)
        host_url = o.hostname
        host_schema = o.scheme
        return f"""{host_schema}://{host_url}"""

    @staticmethod
    def verify_url(url: str) -> bool:
        result = False
        parse_res = urlparse(url)
        curr_host = urlparse(request.base_url)
        if curr_host.hostname == parse_res.hostname:
            return False
        if parse_res.scheme is not None and parse_res.hostname is not None:
            result = True
        return result

    def generate_full_short_urls(self, custom_suffix=None) -> (str, str):
        # generate suffix and host url
        host_url = Url.get_host_url()
        if not custom_suffix:
            l_suffix = randint(5, 7)
            short_suffix = uuid.uuid4().hex[:l_suffix]
            is_capital = randint(0, 1)
            is_upper = randint(0, 1)
            if is_capital == 1:
                short_suffix = short_suffix.capitalize()
            if is_upper:
                short_suffix = short_suffix.upper()
        else:
            short_suffix = custom_suffix

        try:
            if self.already_exists:
                raise SuffixAlreadyExists
            final_url = f"""{host_url}/{short_suffix}"""
        except SuffixAlreadyExists:
            print("This url suffix already exists")
            final_url, short_suffix = None, None

        return final_url, short_suffix

    @staticmethod
    def match_long_url(suffix: str) -> str:
        if suffix in BlockedUrls.BLOCKED_SUFFIXES:
            print(f"Attempt to find a vulnerability detected for {suffix}")
            return '404'

        long_url = check_for_url(suffix)

        return long_url
