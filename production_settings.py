from settings import *
from bundle_config import config

DEBUG = False

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
