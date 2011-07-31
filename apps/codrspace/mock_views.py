"""Mock views for testing OAuth with Github API locally"""


from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

try:
    from local_settings import GITHUB_API_TOKEN
except ImportError:
    # Will always authenticate as 'durden' and only for codrspace app
    GITHUB_API_TOKEN = "1c21852a9f19b685d6f67f4409b5b4980a0c9d4f"


def authorize(request):
    """Fake calling authorize for github api"""

    if 'client_id' not in request.GET:
        raise Exception("Authorize must specify client_id")

    # Just send some code back, doesn't matter for testing
    code = 100
    return redirect("%s?code=%d" % (reverse('signin_callback'), code))


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

    return HttpResponse("access_token=%s&token_type=bearer" % (
                                    GITHUB_API_TOKEN), mimetype="text/plain")
