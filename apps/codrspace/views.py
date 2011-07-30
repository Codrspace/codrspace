"""Main codrspace views"""

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

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


def signout(request):
    if request.user.is_authenticate():
        request.user.logout()
    return redirect(reverse('signout'))


def _validate_github_response(resp):
    """Raise exception if given response has error"""
    if resp.status_code != 200 or 'error' in resp.content:
        raise Exception('code: %u content: %s' % (resp.status_code,
                                                  resp.content))


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
    _validate_github_response(resp)

    # FIXME: Awful parsing w/ lots of assumptions
    # String looks like this currently
    # access_token=1c21852a9f19b685d6f67f4409b5b4980a0c9d4f&token_type=bearer
    token = resp.content.split('&')[0].split('=')[1]
    resp = requests.get('https://api.github.com/user?access_token=%s' % (
                                                                        token))
    # FIXME: Handle error
    _validate_github_response(resp)
    user = simplejson.loads(resp.content)

    try:
        user = user.objects.get(username=user['login'])
    except:
        password = User.objects.make_random_password()
        user = User(username=user['login'], is_active=True,
                    is_superuser=False, password=password)

    user.save()

    profile = user.get_profile()
    profile.git_access_token = token
    profile.save()

    return redirect('http://www.codrspace.com/%s' % (user['login']))
