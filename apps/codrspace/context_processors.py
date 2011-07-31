

def codrspace_contexts(request):
    """
    All custom context vars for codrspace
    """
    contexts = {}
    contexts.update({
        'TAGLINE': "Why you no write tutorial?"
    })

    return contexts
