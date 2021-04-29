from flask_login import UserMixin

from app.db.db_procs import SQLRequest, basic_table_compose


class User(UserMixin):
    """
    User class defines a user data structure and applicable methods.
    """
    def __init__(self, id_, name=None, email=None, status=None, date_added=None, profile_pic=None):
        self.id = id_
        self.name = name
        self.email = email
        self.status = status
        self.date_added = date_added
        self.profile_pic = profile_pic

    def get(self):
        query = f"""SELECT * FROM users WHERE id = '{self.id}'"""

        user = SQLRequest().get_data(query)

        print(f"user: {user}")

        if user is None or len(user) == 0:
            return None

        user = user[0]

        user = User(
            id_=user[0], name=user[1], email=user[2], status=user[3], date_added=user[4], profile_pic=user[5]
        )

        return user

    def create(self) -> None:
        query = "INSERT INTO users (id, name, email, profile_pic) VALUES ('%s', '%s', '%s', '%s')" % (
            self.id, self.name, self.email, self.profile_pic)
        SQLRequest().execute_query(query)

    def drop_user(self) -> bool:
        query = "DELETE FROM users WHERE id='%s'" % self.id
        res = SQLRequest().execute_query(query)
        return res

    def print_info(self) -> None:
        print(
            f"id: {self.id}, name: {self.name}, email: {self.email}, status: {self.status},"
            f" date_added: {self.date_added}, pic: {self.profile_pic}")

    def get_top_user_urls(self) -> dict:
        headers = {'ID': 'text', 'Date added': 'text', 'URL': 'url'}
        q_string = f"SELECT suffix, date_added::TEXT, long_url FROM urls WHERE user_id='{self.id}'" \
                   f" ORDER BY date_added DESC LIMIT 10;"
        return basic_table_compose(headers, q_string)

    def get_most_clicked_urls(self) -> dict:
        headers = {'ID': 'text', 'Clicks': 'text', 'URL': 'url'}
        q_string = f"SELECT suffix, cnt, long_url FROM click_count_view WHERE user_id='{self.id}'" \
                   f" ORDER BY cnt DESC LIMIT 10;"

        return basic_table_compose(headers, q_string)

    def get_user_url_table(self) -> dict:
        headers = {'Short URL': 'text', 'Description': 'text', 'URL': 'url', 'Date added': 'text',
                   'Clicks': 'text', 'Actions': 'text'}
        q_string = f"select suffix, description, long_url, date_added::TEXT, cnt " \
                   f"from all_url_info where user_id='{self.id}' order by date_added asc;"
        return basic_table_compose(headers, q_string)
