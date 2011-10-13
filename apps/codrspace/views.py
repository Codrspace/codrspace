"""Main codrspace views"""
import requests
import os
from datetime import datetime
from hashlib import md5
from time import time

from django.http import Http404, HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from django.db.models import Q

from codrspace.models import Post, Profile, Media
from codrspace.forms import PostForm, MediaForm


class GithubAuthError(Exception):
    pass


def index(request, template_name="home.html"):
    return render(request, template_name)


def post_detail(request, username, slug, template_name="post_detail.html"):
    user = get_object_or_404(User, username=username)

    post = get_object_or_404(
        Post,
        author=user,
        slug=slug,)

    if post.status == 'draft':
        if post.author != request.user:
            raise Http404

    return render(request, template_name, {
        'username': username,
        'post': post,
        'meta': user.profile.get_meta(), })


def post_list(request, username, template_name="post_list.html"):
    user = get_object_or_404(User, username=username)

    posts = Post.objects.filter(
        Q(status="published") | Q(status="draft"),
        author=user
    )
    posts = posts.order_by('-pk')

    return render(request, template_name, {
        'username': username,
        'posts': posts,
        'meta': user.profile.get_meta(),
    })


@login_required
def add(request, template_name="add.html"):
    """ Add a post """

    posts = Post.objects.filter(author=request.user).order_by('-pk')
    media_set = Media.objects.filter(uploader=request.user).order_by('-pk')
    media_form = MediaForm()

    if request.method == "POST":
        # media
        media_form = MediaForm(request.POST, request.FILES)
        if media_form.is_valid():
            media = media_form.save(commit=False)
            media.uploader = request.user
            media.filename = unicode(media_form.cleaned_data.get('file', ''))
            media.save()

        # post
        form = PostForm(request.POST)
        if form.is_valid() and 'submit_post' in request.POST:
            post = form.save(commit=False)

            # if something to submit
            if post.title or post.content:
                post.author = request.user
                if post.status == 'published':
                    post.publish_dt = datetime.now()
                post.save()
                messages.info(
                    request,
                    'Added post %s successfully.' % post)
                return redirect('edit', pk=post.pk)

    else:
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
    post = get_object_or_404(Post, pk=pk, author=request.user)
    posts = Post.objects.filter(author=request.user).order_by('-pk')
    media_set = Media.objects.filter(uploader=request.user).order_by('-pk')
    media_form = MediaForm()

    if request.method == "POST":

        # media post
        if 'file' in request.FILES:
            media_form = MediaForm(request.POST, request.FILES)
            if media_form.is_valid():
                media = media_form.save(commit=False)
                media.uploader = request.user
                media.filename = unicode(media_form.cleaned_data.get(
                                                                'file', ''))
                media.save()

        # post post  hehe
        if 'title' in request.POST:
            form = PostForm(request.POST, instance=post)
            if form.is_valid() and 'submit_post' in request.POST:
                post = form.save(commit=False)
                if post.status == 'published':
                    if not post.publish_dt:
                        post.publish_dt = datetime.now()
                if post.status == "draft":
                    post.publish_dt = None
                post.save()
                messages.info(
                    request,
                    'Edited post %s successfully.' % post)
                return render(request, template_name, {
                    'form': form,
                    'post': post,
                    'posts': posts,
                    'media_set': media_set,
                    'media_form': media_form,
                })

            return render(request, template_name, {
                'form': form,
                'post': post,
                'posts': posts,
                'media_set': media_set,
                'media_form': media_form,
            })

    form = PostForm(instance=post)
    return render(request, template_name, {
        'form': form,
        'post': post,
        'posts': posts,
        'media_set': media_set,
        'media_form': media_form,
    })


def signin_start(request, slug=None, template_name="signin.html"):
    """Start of OAuth signin"""

    return redirect('%s?client_id=%s&redirect_uri=%s' % (
                    settings.GITHUB_AUTH['auth_url'],
                    settings.GITHUB_AUTH['client_id'],
                    settings.GITHUB_AUTH['callback_url']))


def signout(request):
    if request.user.is_authenticated():
        logout(request)
    return redirect(reverse('homepage'))


def _validate_github_response(resp):
    """Raise exception if given response has error"""

    if resp.error is not None:
        raise GithubAuthError('Could not communicate with Github API (%s)' % (
                                                            resp.error.reason))

    if resp.status_code != 200 or 'error' in resp.content:
        raise GithubAuthError('code: %u content: %s' % (resp.status_code,
                                                  resp.content))


def _parse_github_access_token(content):
    """Super hackish way of parsing github access token from request"""
    # FIXME: Awful parsing w/ lots of assumptions
    # String looks like this currently
    # access_token=1c21852a9f19b685d6f67f4409b5b4980a0c9d4f&token_type=bearer
    return content.split('&')[0].split('=')[1]


def signin_callback(request, slug=None, template_name="base.html"):
    """Callback from Github OAuth"""

    try:
        code = request.GET['code']
    except KeyError:
        return render(request, 'auth_error.html', dictionary={
                            'err': 'Unable to get request code from Github'})

    resp = requests.post(url=settings.GITHUB_AUTH['access_token_url'],
                         data={'client_id': settings.GITHUB_AUTH['client_id'],
                               'client_secret': settings.GITHUB_AUTH['secret'],
                               'code': code})

    try:
        _validate_github_response(resp)
    except GithubAuthError, err:
        return render(request, 'auth_error.html', dictionary={'err': err})

    token = _parse_github_access_token(resp.content)

    # Don't use token unless running in production b/c mocked service won't
    # know a valid token
    user_url = settings.GITHUB_AUTH['user_url']

    if not settings.GITHUB_AUTH['debug']:
        user_url = '%s?access_token=%s' % (user_url, token)

    resp = requests.get(user_url)

    try:
        _validate_github_response(resp)
    except GithubAuthError, err:
        return redirect(reverse('auth_error', args=[err]))

    github_user = simplejson.loads(resp.content)

    try:
        user = User.objects.get(username=github_user['login'])
    except:
        password = User.objects.make_random_password()
        user_defaults = {
            'username': github_user['login'],
            'is_active': True,
            'is_superuser': False,
            'password': password}

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

        # Fake auth b/c github already verified them and we aren't using our
        # own #passwords...yet?
        user.auto_login = True
        user = authenticate(user=user)
        login(request, user)

    return redirect(reverse('post_list', args=[user.username]))
