"""Main codrspace views"""

from django.shortcuts import render, redirect
from settings import GITHUB_CLIENT_ID

import requests


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

    code = request.GET['code']
    resp = requests.post(url='https://github.com/login/oauth/access_token',
                        params={
                            'client_id': GITHUB_CLIENT_ID,
                            'client_secret':
                                '2b40ac4251871e09441eb4147cbd5575be48bde9',
                            'code': code})
    # FIXME: Handle error
    if resp.status_code != 200 or 'error' in resp.content:
        raise Exception('code: %u content: %s' % (resp.status_code,
                                                  resp.content))

    token = resp.content
    return redirect('http://www.codrspace.com/%s' % (token))
