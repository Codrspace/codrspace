"""Main codrspace views"""

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from settings import GITHUB_CLIENT_ID


def index(request, slug=None, template_name="base.html"):
    return render_to_response(template_name, {},
        context_instance=RequestContext(request))


def signin_start(request, slug=None, template_name="signin.html"):
    """Start of OAuth signin"""
    return redirect('https://github.com/login/oauth/authorize?client_id=%s' % (
                    GITHUB_CLIENT_ID))


def signin_callback(request, slug=None, template_name="base.html"):
    """Callback from Github OAuth"""
    return render_to_response(template_name, {}, )
