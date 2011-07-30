"""Main codrspace views"""

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from settings import GITHUB_CLIENT_ID, DEBUG
from codrspace.models import Post
from codrspace.forms import PostForm
from profile.models import Profile

import requests


def index(request):

    if request.user.is_authenticated(): template_name = "auth_base.html"
    else: template_name = "anon_base.html"

    codr_spaces = Post.objects.all().order_by('-pk')

    return render(request, template_name, {
        'codr_spaces':codr_spaces,
    })


def add(request, template_name="add.html"):
    """ Add a post """

    codr_spaces = Post.objects.all().order_by('-pk')

    if request.method == "POST":
        form = CodrForm(request.POST)
        if form.is_valid():
            codr_space = form.save()
            return render(request, template_name, {'form': form, 'codr_spaces': codr_spaces})

    form = CodrForm()
    return render(request, template_name, {'form': form, 'codr_spaces': codr_spaces})


def edit(request, pk=0, template_name="edit.html"):
    """ Edit a post """
    codr_space = get_object_or_404(Post, pk=pk)
    codr_spaces = Post.objects.all().order_by('-pk')

    print 'codr_space', codr_space.title, codr_space.content

    if request.method == "POST":
        form = CodrForm(request.POST, instance=codr_space)

        if form.is_valid():
            codr_space = form.save()

            return render(request, template_name, {
                'form':form, 
                'codr_space':codr_space,
                'codr_spaces':codr_spaces
            })

    form = CodrForm(instance=codr_space)
    return render(request, template_name, {
        'form':form,
        'codr_space':codr_space,
        'codr_spaces':codr_spaces
    })


def signin_start(request, slug=None, template_name="signin.html"):
    """Start of OAuth signin"""

    url = 'https://github.com/login/oauth/authorize'
    if DEBUG:
        url = 'http://localhost:8000/authorize'

    return redirect('%s?client_id=%s' % (url, GITHUB_CLIENT_ID))


def signout(request):
    if request.user.is_authenticated():
        logout(request)
    return redirect(reverse('homepage'))


def _validate_github_response(resp):
    """Raise exception if given response has error"""

    # FIXME: Handle error
    if resp.status_code != 200 or 'error' in resp.content:
        raise Exception('code: %u content: %s' % (resp.status_code,
                                                  resp.content))

def _parse_github_access_token(content):
    """Super hackish way of parsing github access token from request"""
    # FIXME: Awful parsing w/ lots of assumptions
    # String looks like this currently
    # access_token=1c21852a9f19b685d6f67f4409b5b4980a0c9d4f&token_type=bearer
    return content.split('&')[0].split('=')[1]


def signin_callback(request, slug=None, template_name="base.html"):
    """Callback from Github OAuth"""

    user = None
    url = 'https://github.com/login/oauth/access_token'
    if DEBUG:
        url = 'http://localhost:9000/access_token/'

    code = request.GET['code']
    resp = requests.post(url=url, data={
                        'client_id': GITHUB_CLIENT_ID,
                        'client_secret':
                        '2b40ac4251871e09441eb4147cbd5575be48bde9',
                        'code': code})

    _validate_github_response(resp)

    # FIXME: Awful parsing w/ lots of assumptions
    # String looks like this currently
    # access_token=1c21852a9f19b685d6f67f4409b5b4980a0c9d4f&token_type=bearer
    token = resp.content.split('&')[0].split('=')[1]
    resp = requests.get(
        'https://api.github.com/user?access_token=%s' % (
        token
    ))

    # FIXME: Handle error
    _validate_github_response(resp)
    github_user = simplejson.loads(resp.content)

    try:
        user = User.objects.get(username=github_user['login'])
    except:
        password = User.objects.make_random_password()
        user_defaults = {
            'username': github_user['login'],
            'is_active': True,
            'is_superuser': False,
            'password': password
        }
        user = User(**user_defaults)

    if user:
        user.save()
        try:
            profile = user.get_profile()
        except:
            profile = Profile(git_access_token=token, user=user)

        profile.git_access_token = token
        profile.save()

        # Fake auth b/c github already verified them and we aren't using our own
        # passwords...yet?
        user.auto_login = True
        user = authenticate(user=user)
        login(request, user)

    return redirect(reverse('homepage'))
