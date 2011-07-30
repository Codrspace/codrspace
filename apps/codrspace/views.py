from django.shortcuts import render
from django.template import RequestContext


def index(request, slug=None, template_name="base.html"):
    return render(request, template_name)
