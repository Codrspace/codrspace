"""Main codrspace views"""
import requests
from datetime import datetime

from StringIO import StringIO
from zipfile import ZipFile

from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import simplejson
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from codrspace.models import Post, Profile, Media, Setting
from codrspace.forms import PostForm, MediaForm, \
                            SettingForm, FeedBackForm


class GithubAuthError(Exception):
    pass


def index(request, template_name="home_shutdown.html"):
    return render(request, template_name)


def post_detail(request, username, slug, template_name="post_detail.html"):
    user = get_object_or_404(User, username=username)

    post = get_object_or_404(
        Post,
        author=user,
        slug=slug,)

    try:
        user_settings = Setting.objects.get(user=user)
    except:
        user_settings = None

    if post.status == 'draft':
        if post.author != request.user:
            raise Http404

    return render(request, template_name, {
        'username': username,
        'post': post,
        'meta': user.profile.get_meta(),
        'user_settings': user_settings
    })


def post_list(request, username, post_type='published',
              template_name="post_list_shutdown.html"):
    user = get_object_or_404(User, username=username)

    try:
        user_settings = Setting.objects.get(user=user)
    except:
        user_settings = None

    if post_type == 'published':
        post_type = 'posts'
        status_query = Q(status="published")
    else:
        post_type = 'drafts'
        status_query = Q(status="draft")

    posts = Post.objects.filter(
        status_query,
        Q(publish_dt__lte=datetime.now()) | Q(publish_dt=None),
        author=user,
    )
    posts = posts.order_by('-publish_dt')

    # paginate posts
    paginator = Paginator(posts, 3)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        posts = paginator.page(paginator.num_pages)

    return render(request, template_name, {
        'username': username,
        'posts': posts,
        'post_type': post_type,
        'meta': user.profile.get_meta(),
        'user_settings': user_settings
    })

@login_required
def drafts(request):
    return post_list(request, request.user.username, post_type='drafts')


@login_required
def add(request, template_name="add.html"):
    """ Add a post """

    posts = Post.objects.filter(
        author=request.user,
        status__in=['draft', 'published']
    ).order_by('-pk')
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
            messages.info(
                request,
                'Media %s has been uploaded.' % media.filename,
                extra_tags='alert-success'
            )

        # post
        form = PostForm(request.POST, user=request.user)
        if form.is_valid() and 'submit_post' in request.POST:
            post = form.save(commit=False)

            # if something to submit
            if post.title or post.content:
                post.author = request.user
                if post.status == 'published' and not post.publish_dt:
                    post.publish_dt = datetime.now()
                post.save()
                messages.info(
                    request,
                    'Added post "%s".' % post,
                    extra_tags='alert-success')
                return redirect('edit', pk=post.pk)

    else:
        form = PostForm(user=request.user)

    return render(request, template_name, {
        'form': form,
        'posts': posts,
        'media_set': media_set,
        'media_form': media_form,
    })


@login_required
def user_settings(request, template_name="settings.html"):
    """ Add/Edit a setting """

    user = get_object_or_404(User, username=request.user.username)

    try:
        settings = Setting.objects.get(user=user)
    except Setting.DoesNotExist:
        settings = None

    form = SettingForm(instance=settings)

    if request.method == 'POST':
        form = SettingForm(request.POST, instance=settings)
        if form.is_valid():
            msg = "Edited settings successfully."
            messages.info(request, msg, extra_tags='alert-success')
            settings = form.save(commit=False)
            settings.user = user
            settings.save()

            # clear settings cache
            cache_key = '%s_user_settings' % user.pk
            cache.set(cache_key, None)

    return render(request, template_name, {
        'form': form,
    })


@login_required
def api_settings(request, template_name="api_settings.html"):
    """ View API settings """

    from tastypie.models import ApiKey
    api_key = get_object_or_404(ApiKey, user=request.user)

    return render(request, template_name, {
        'api_key': api_key,
    })


@login_required
def delete(request, pk=0, template_name="delete.html"):
    """ Delete a post """
    post = get_object_or_404(Post, pk=pk, author=request.user)
    user = get_object_or_404(User, username=request.user.username)

    if request.method == 'POST':
        if 'delete-post' in request.POST:
            post.status = 'deleted'
            post.save()

            messages.info(request, 'Post deleted', extra_tags='alert-success')

            return redirect(reverse('post_list', args=[user.username]))

    return render(request, template_name, {
        'post': post,
    })


@login_required
def edit(request, pk=0, template_name="edit.html"):
    """ Edit a post """
    post = get_object_or_404(Post, pk=pk, author=request.user)
    posts = Post.objects.filter(
        ~Q(id=post.pk),
        author=request.user,
        status__in=['draft', 'published']
    ).order_by('-pk')
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
            form = PostForm(request.POST, instance=post, user=request.user)
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
                    'Edited post "%s".' % post,
                    extra_tags='alert-success')
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

    form = PostForm(instance=post, user=request.user)
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

        # Get/Create the user profile
        try:
            profile = user.get_profile()
        except:
            profile = Profile(
                git_access_token=token,
                user=user,
                meta=resp.content
            )

        # update meta information and token
        profile.git_access_token = token
        profile.meta = resp.content
        profile.save()

        # Create settings for user
        try:
            user_settings = Setting.objects.get(user=user)
        except:
            user_settings = None

        if not user_settings:
            s = Setting()
            s.user = user
            s.timezone = "US/Central"
            s.save()

        # Fake auth b/c github already verified them and we aren't using our
        # own #passwords...yet?
        user.auto_login = True
        user = authenticate(user=user)
        login(request, user)

    return redirect(reverse('post_list', args=[user.username]))


@login_required
def feedback(request, template_name='feedback.html'):
    """ Send Feed back """
    from django.core.mail import EmailMessage
    user = get_object_or_404(User, username=request.user.username)

    form = FeedBackForm(initial={'email': user.email})

    if request.method == 'POST':
        form = FeedBackForm(request.POST)
        if form.is_valid():
            msg = "Thanks for send us feedback. We hope to make the product better."
            messages.info(request, msg, extra_tags='alert-success')

            subject = 'Codrspace feedback from %s' % user.username
            message = '%s (%s), %s' % (
                request.user.username,
                form.cleaned_data['email'],
                form.cleaned_data['comments'],
            )

            email = EmailMessage(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.SERVER_EMAIL,],
                headers = {'Reply-To': form.cleaned_data['email']}
            )
            email.send(fail_silently=False)

    return render(request, template_name, {
        'form': form,
    })

@login_required
def posts_download(request, username):
    """Download all posts as an archive"""
    user = get_object_or_404(User, username=username)

    try:
        user_settings = Setting.objects.get(user=user)
    except:
        user_settings = None

    posts = Post.objects.filter(author=user)
    io_buffer = StringIO()
    zip = ZipFile(io_buffer, "a")

    for post in posts:
        zip.writestr("{}.md".format(post.slug), post.content.encode('utf-8'))

    # fix for Linux zip files read in Windows
    for file in zip.filelist:
        file.create_system = 0    

    zip.close()

    response = HttpResponse(mimetype="application/zip")
    response["Content-Disposition"] = "attachment; filename=codrspace_post_archive_{}.zip".format(username)

    io_buffer.seek(0)
    response.write(io_buffer.read())

    return response


@login_required
def render_preview(request, template_name='preview.html'):
    """Ajax view for rendering preview of post"""

    # make a mock post
    post = {
        'title': '',
        'content': ''
    }

    if request.method == 'POST':
        if 'title' in request.POST:
            post['title'] = request.POST['title']
        if 'content' in request.POST:
            post['content'] = request.POST['content']

    return render(request, template_name, {
        'post': post,
    })


def donate(request, template_name='donate.html'):
    return render(request, template_name)

def help(request, template_name='help.html'):
    return render(request, template_name)

def handler500(request, template_name='500.html'):
    response = render(request, template_name)
    response.status_code = 500
    return render(request, template_name)
