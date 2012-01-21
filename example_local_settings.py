"""
The following settings are meant to be used for a faked github.com OAuth
instance.  You should rename this file to 'local_settings.py' in order to use
it for the instance it resides in.

The are 2 main reasons for using local_settings.py when running locally:
    1. Disable CSRF protection (just not necessary when running on localhost)
    2. Disable file-based caching (who cares if things are slower when coding!)
        - Feel free to run with caching enabled locally, but it can cause
          headaches when developing because models, etc. are always changing so
          it doesn't serve a lot of purpose.
"""


from frappy.services.github import Github

def get_setting(setting):
    """
    Get a setting from settings.py
    """
    import settings
    return getattr(settings, setting)

# Development debug mode
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Replace with your own github credentials to run locally and have your profile
# filled out automatically without an access token from the fake Oauth instance
GITHUB_AUTH = {
    'client_id': 'doesntmatter',
    'secret': 'doesntmatter',
    'callback_url': 'http://127.0.0.1:8000/signin_callback',
    'auth_url': 'http://127.0.0.1:9000/authorize/',
    'access_token_url': 'http://127.0.0.1:9000/access_token/',

    # Get information of authenticated user
    'user_url': 'http://127.0.0.1:9000/fake_user/',

    # User that is 'logged in' by fake api setup
    'username': 'octocat',

    # Debug mode - for faking auth_url
    'debug': True
}

# set this to the JSON that comes back from http://api.github.com/user/
user = Github().users(GITHUB_AUTH['username'])
GITHUB_USER_JSON = user.response_json


# Overrides for middleware to avoid having the CSRF protection when running
# locally
MIDDLEWARE_CLASSES = get_setting('MIDDLEWARE_CLASSES')
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

# Disable caching
CACHES = get_setting('CACHES')
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
