from django.conf import settings


def codrspace_contexts(request):
    """
    All custom context vars for codrspace
    """
    contexts = {}
    contexts.update({
        'SITE_URL': settings.SITE_URL,
    })

    return contexts
