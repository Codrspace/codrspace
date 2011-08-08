

def codrspace_contexts(request):
    """
    All custom context vars for codrspace
    """
    contexts = {}
    contexts.update({'TAGLINE': "Write about matters, code."})

    return contexts
