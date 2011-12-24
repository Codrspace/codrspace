from django.db.models import Manager
from django.core.cache import cache


class SettingManager(Manager):
    """
    Manager model for settings
    """
    def get(self, *args, **kwargs):
        user_pk = None
        user_settings = None
        cache_key = None

        # get user information if passed
        if 'user' in kwargs:
            user = kwargs['user']
            if not user.is_anonymous():
                user_pk = kwargs['user'].pk

        # set a cache key for this user
        if user_pk:
            cache_key = '%s_user_settings' % user_pk
            user_settings = cache.get(cache_key)

            if not user_settings:
                user_settings = super(SettingManager, self).get(*args, **kwargs)
                cache.set(cache_key, user_settings)
        else:
            user_settings = super(SettingManager, self).get(*args, **kwargs)

        return user_settings
