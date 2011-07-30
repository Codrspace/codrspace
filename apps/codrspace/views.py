"""Main codrspace views"""

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from settings import GITHUB_CLIENT_ID, DEBUG
from codrspace.models import Post
from codrspace.forms import PostForm
from codrspace.models import Profile

import requests


def index(request, template_name="home.html"):
    if request.user.is_authenticated():
        redirect(reverse("post_index", args=[request.user.username]))

    return render(request, template_name)


def post_index(request, template_name="post_index.html"):
    posts = Post.objects.filter(author=request.user.username)
    posts = posts.order_by('-pk')

    return render(request, template_name, {
        'posts': posts,
    })


def add(request, template_name="add.html"):
    """ Add a post """
    posts = Post.objects.all().order_by('-pk')

    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save()
            return render(request, template_name, {'form': form, 'posts': posts})

    form = PostForm()
    return render(request, template_name, {'form': form, 'posts': posts})


def edit(request, pk=0, template_name="edit.html"):
    """ Edit a post """
    post = get_object_or_404(Post, pk=pk)
    posts = Post.objects.all().order_by('-pk')

    if request.method == "POST":
        form = PostForm(request.POST, instance=codr_space)

        if form.is_valid():
            post = form.save()

            return render(request, template_name, {
                'form': form, 
                'post': post,
                'posts': posts
            })

    form = PostForm(instance=post)
    return render(request, template_name, {
        'form': form,
        'post': post,
        'posts': posts
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
