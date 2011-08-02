from settings import *
from bundle_config import config

DEBUG = True

# Media and Static file
MEDIA_ROOT = os.path.join(os.getenv('EPIO_DATA_DIRECTORY', PROJECT_ROOT), 'media')
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'site_media/static/')

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
