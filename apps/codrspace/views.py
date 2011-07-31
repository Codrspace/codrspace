"""Main codrspace views"""

from datetime import datetime
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from settings import GITHUB_CLIENT_ID, DEBUG
from codrspace.models import Post, Profile, Media
from codrspace.forms import PostForm, MediaForm

import requests


def index(request, template_name="home.html"):
    return render(request, template_name)


def post_detail(request, username, slug, template_name="post_detail.html"):
    user = get_object_or_404(User, username=username)

    post = get_object_or_404(
        Post,
        author=user,
        slug=slug,
    )

    if post.status == 'draft':
        if post.status != request.user:
            raise Http404

    return render(request, template_name, {
        'post': post,
        'meta': user.profile.get_meta(),
    })


@login_required
def post_list(request, username, template_name="post_list.html"):
    user = get_object_or_404(User, username=username)

    posts = Post.objects.filter(author=user, status="published")
    posts = posts.order_by('-pk')

    return render(request, template_name, {
        'posts': posts,
        'meta': user.profile.get_meta(),
    })


@login_required
def add(request, template_name="add.html"):
    """ Add a post """

    posts = Post.objects.filter(author=request.user).order_by('-pk')
    media_set = Media.objects.filter(uploader=request.user).order_by('-pk')
    media_form = MediaForm()

    if hasattr(request, 'FILES'):
        media_form = MediaForm(request.POST, request.FILES)
        if media_form.is_valid():
            media = media_form.save(commit=False)
            media.uploader = request.user
            media.filename = unicode(media_form.cleaned_data.get('file', ''))
            media.save()

    if request.method == "POST":
        form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user

            if post.status == 'published':
                post.publish_dt = datetime.now()

            post.save()
            return redirect('edit', pk=post.pk)

    form = PostForm()
    return render(request, template_name, {
        'form': form, 
        'posts': posts,
        'media_set': media_set,
        'media_form': media_form,
    })


@login_required
def edit(request, pk=0, template_name="edit.html"):
    """ Edit a post """
    post = get_object_or_404(Post, pk=pk)
    posts = Post.objects.filter(author=request.user).order_by('-pk')
    media_set = Media.objects.filter(uploader=request.user).order_by('-pk')
    media_form = MediaForm()

    if hasattr(request, 'FILES'):
        media_form = MediaForm(request.POST, request.FILES)
        if media_form.is_valid():
            media = media_form.save(commit=False)
            media.uploader = request.user
            media.filename = unicode(media_form.cleaned_data.get('file', ''))
            media.save()

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)

        if form.is_valid():
            post = form.save(commit=False)

            if post.status == 'published':
                if not post.publish_dt:
                    post.publish_dt = datetime.now()

            if post.status == "draft":
                post.publish_dt = None;
            
            post.save()
            return render(request, template_name, {
                'form':form, 
                'post':post,
                'posts':posts,
                'media_set': media_set,
                'media_form': media_form,
            })

    form = PostForm(instance=post)
    return render(request, template_name, {
        'form':form,
        'post':post,
        'posts':posts,
        'media_set': media_set,
        'media_form': media_form,
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
            profile = Profile(git_access_token=token, user=user,
                              meta=resp.content)

        profile.git_access_token = token
        profile.save()

        # Fake auth b/c github already verified them and we aren't using our own
        # passwords...yet?
        user.auto_login = True
        user = authenticate(user=user)
        login(request, user) 

    return redirect(reverse('post_list', args=[user.username]))
