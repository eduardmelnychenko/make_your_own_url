class DbSecrets:
    DB_NAME = 'postgres'
    DB_PORT = 5432
    HOST = 'make_your_own_url_db'
    USERNAME = 'postgres'
    PASSWORD = 'postgres'


class GoogleSecrets:
    GOOGLE_CLIENT_ID = 'YOU_ID.apps.googleusercontent.com'
    GOOGLE_CLIENT_SECRET = 'YOUR_SECRET'
    GOOGLE_DISCOVERY_URL = 'https://accounts.google.com/.well-known/openid-configuration'


class CacheSecrets:
    pass


class CelerySecrets:
    pass


class BlockedUrls:
    BLOCKED_SUFFIXES = ('wp-login.php', 'wordpress/wp-login.php',
                        'blog/wp-login.php', 'wp/wp-login.php')