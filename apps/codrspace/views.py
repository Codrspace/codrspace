"""Main codrspace views"""

from django.shortcuts import render, redirect
from settings import GITHUB_CLIENT_ID


def index(request, slug=None, template_name="base.html"):
    return render(request, template_name)


def edit(request, slug=None, template_name="edit.html"):
    """Edit Your Post"""
    return render(request, template_name, {})


def signin_start(request, slug=None, template_name="signin.html"):
    """Start of OAuth signin"""
    return redirect('https://github.com/login/oauth/authorize?client_id=%s' % (
                    GITHUB_CLIENT_ID))


def signin_callback(request, slug=None, template_name="base.html"):
    """Callback from Github OAuth"""
    print request.GET
