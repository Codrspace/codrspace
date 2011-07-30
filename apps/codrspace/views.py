<<<<<<< HEAD
from django.shortcuts import render
=======
"""Main codrspace views"""

from django.shortcuts import render_to_response, redirect
>>>>>>> ce96d1c209bb5f2d3359681c7fac7d8bd3fceb84
from django.template import RequestContext
from settings import GITHUB_CLIENT_ID


def index(request, slug=None, template_name="base.html"):
<<<<<<< HEAD
    return render(request, template_name)
=======
    return render_to_response(template_name, {},
        context_instance=RequestContext(request))


def signin_start(request, slug=None, template_name="signin.html"):
    """Start of OAuth signin"""
    return redirect('https://github.com/login/oauth/authorize?client_id=%s' % (
                    GITHUB_CLIENT_ID))


def signin_callback(request, slug=None, template_name="base.html"):
    """Callback from Github OAuth"""
<<<<<<< HEAD
    return render_to_response(template_name, {}, )
>>>>>>> ce96d1c209bb5f2d3359681c7fac7d8bd3fceb84
=======
    print request.GET
>>>>>>> 5ccdd9fa87aabf074ad18261f14d2207e99402d7
