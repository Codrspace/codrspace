from django.conf import settings
from codrspace.models import Setting


def codrspace_contexts(request):
    """
    All custom context vars for codrspace
    """
    user_settings = None
    contexts = {}

    # add SITE_TAGLINE, and SITE_NAME to the context
    contexts.update({'SITE_TAGLINE': settings.SITE_TAGLINE})
    contexts.update({'SITE_NAME': settings.SITE_NAME})

    # add user settings to the context
    if not request.user.is_anonymous:
        try:
            user_settings = Setting.objects.get(user=request.user)
        except Setting.DoesNotExist:
            user_settings = None

    contexts.update({'user_settings': user_settings})

    return contexts
