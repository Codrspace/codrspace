from django.conf import settings
from django.core.cache import cache

from codrspace.models import SystemNotification


def get_system_notifications():
    notifications = cache.get('system_notifications')

    if not notifications:
        notifications = SystemNotification.objects.filter(enabled=True)
        cache.set('system_notifications', notifications, 86400)

    return notifications


def codrspace_contexts(request):
    """
    All custom context vars for codrspace
    """
    contexts = {}

    # add SITE_TAGLINE, and SITE_NAME, and VERSION to the context
    contexts.update({'SITE_TAGLINE': settings.SITE_TAGLINE})
    contexts.update({'SITE_NAME': settings.SITE_NAME})
    contexts.update({'VERSION': settings.VERSION})
    contexts.update({'ANALYTICS_CODE': settings.ANALYTICS_CODE})
    contexts.update({'SITE_URL': settings.SITE_URL})
    contexts.update({'SYSTEM_NOTIFICATIONS': get_system_notifications() })

    return contexts
