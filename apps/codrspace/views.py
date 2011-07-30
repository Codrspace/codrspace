"""Main codrspace views"""

from django.shortcuts import render, redirect, get_object_or_404
from settings import GITHUB_CLIENT_ID
from codrspace.models import CodrSpace
from codrspace.forms import CodrForm

import requests


def index(request, template_name="base.html"):
    return render(request, template_name)

def add(request, template_name="add.html"):
    """ Add a post """
    if request.method == "POST":
        form = CodrForm(request.POST, user=request.user)
        if form.is_valid(): 
            codr_space = form.save(commit=False)
            return render(request, template_name, {'form':form})

    form = CodrForm()
    return render(request, template_name, {'form':form})


def edit(request, pk=0, template_name="edit.html"):
    """ Edit a post """
    codr_space = get_object_or_404(CodrSpace, pk=pk)

    if request.method == "POST":
        form = CodrForm(request.POST, instance=codr_space, user=request.user)

        if form.is_valid():
            codr_space = form.save(commit=False)
            return render(request, template_name, {'form':form})

    form = CodrForm()
    return render(request, template_name, {'form':form})


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

    # FIXME: Awful parsing w/ lots of assumptions
    # String looks like this currently
    # access_token=1c21852a9f19b685d6f67f4409b5b4980a0c9d4f&token_type=bearer
    token = resp.content.split('&')[0].split('=')[1]
    return redirect('http://www.codrspace.com/%s' % (token))
