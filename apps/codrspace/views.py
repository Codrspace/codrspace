from django.shortcuts import render_to_response
from django.template import RequestContext


def index(request, slug=None, template_name="base.html"):
    return render_to_response(template_name, {},
        context_instance=RequestContext(request))
