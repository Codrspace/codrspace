from settings import *
from bundle_config import config

DEBUG = False

# Media and Static file
MEDIA_ROOT = os.path.join(os.getenv('EPIO_DATA_DIRECTORY', PROJECT_ROOT),
                                                                    'media')
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'site_media/static/')

# Github setup
GITHUB_AUTH = {
    'client_id': '003358f749bdb9e47e3a',
    'secret': '057267fc8e1569cb0e41a9c1e692834df0c91ace',
    'callback_url': 'http://codrspace.ep.io/signin_callback',
    'auth_url': 'https://github.com/login/oauth/authorize',
    'access_token_url': 'https://github.com/login/oauth/access_token',

    # Get information of authenticated user
    'user_url': 'https://api.github.com/user',
}

# Database Settings
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "HOST": config['postgres']['host'],
        "PORT": int(config['postgres']['port']),
        "USER": config['postgres']['username'],
        "PASSWORD": config['postgres']['password'],
        "NAME": config['postgres']['database'],
    },
}

# Redis Caching
CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': '{host}:{port}'.format(
                host=config['redis']['host'],
                port=config['redis']['port']),
        'OPTIONS': {
            'PASSWORD': config['redis']['password'],
        },
        'VERSION': config['core']['version'],
    },
}
