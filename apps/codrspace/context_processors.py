from django.conf import settings


def codrspace_contexts(request):
    """
    All custom context vars for codrspace
    """
    contexts = {}

    # add SITE_TAGLINE, and SITE_NAME to the context
    contexts.update({'SITE_TAGLINE': settings.SITE_TAGLINE})
    contexts.update({'SITE_NAME': settings.SITE_NAME})

    return contexts
