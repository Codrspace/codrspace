"""Mock views for testing OAuth with Github API locally"""


from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.conf import settings


def fake_user(request):
    """Fake user data for the user"""

    if not hasattr(settings, 'GITHUB_USER_JSON'):
        raise Exception('GITHUB_USER_JSON must be set for fake user data')

    if not settings.GITHUB_USER_JSON:
        raise Exception('GITHUB_USER_JSON must contain github user JSON data')

    return HttpResponse(settings.GITHUB_USER_JSON, mimetype="application/json", status=200)


def authorize(request):
    """Fake calling authorize for github api"""

    if 'client_id' not in request.GET:
        raise Exception("Authorize must specify client_id")

    # Assume 200 and debugging github url
    code = 200
    callback_url = settings.GITHUB_AUTH['callback_url']

    return redirect("%s?code=%d" % (callback_url, code))


def access_token(request):
    """Fake calling method to get access token for github api"""

    if request.method != 'POST':
        raise Exception("Must use POST request")

    if 'client_id' not in request.POST:
        raise Exception("Authorize must specify client_id")

    if 'client_secret' not in request.POST:
        raise Exception("Authorize must specify client_secret")

    if 'code' not in request.POST:
        raise Exception("Authorize must specify code")

    # Just using junk for token b/c it won't be used locally, just need to get
    # the flow
    token = '2341342fdsffkjl234'
    return HttpResponse("access_token=%s&token_type=bearer" % (token),
                        mimetype="text/plain")
