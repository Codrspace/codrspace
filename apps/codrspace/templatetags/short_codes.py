"""Custom filters to grab code from the web via short codes"""


import requests
import mimetypes
import re
import os
import markdown

from django.utils import simplejson
from django import template
from django.utils.safestring import mark_safe

from settings import MEDIA_ROOT

from codrspace.templatetags.syntax_color import _colorize_table

register = template.Library()


@register.filter(name='explosivo')
def explosivo(value):
    """
    Search text for any references to supported short codes and explode them
    """

    # Round-robin through all functions as if they are filter methods so we
    # don't have to update some silly list of available ones when they are
    # added
    import sys, types
    module = sys.modules[__name__]
    
    for name, var in vars(module).items():
        if type(var) == types.FunctionType and name.startswith('filter_'):
            value, match = var(value)
            if not match:
                value = markdown.markdown(value)

    return mark_safe(value)


def filter_gist(value):
    pattern = re.compile('\[gist (\d+) *\]', flags=re.IGNORECASE)

    match = re.search(pattern, value)
    if match is None:
        return value, None

    gist_id = int(match.group(1))
    resp = requests.get('https://api.github.com/gists/%d' % (gist_id))

    if resp.status_code != 200:
        return value

    content = simplejson.loads(resp.content)
    gist_text = ""

    # Go through all files in gist and smash 'em together
    for name in content['files']:
        gist_text += "%s" % (
            _colorize_table(content['files'][name]['content'], None)
        )

    return (re.sub(pattern, gist_text, markdown.markdown(value)), match)


def filter_url(value):
    pattern = re.compile('\[url (\S+) *\]', flags=re.IGNORECASE)

    match = re.search(pattern, value)
    if match is None:
        return value, None

    url = match.group(1)

    # FIXME: Validate that value is actually a url
    resp = requests.get(url)

    if resp.status_code != 200:
        return value

    return (re.sub(pattern, _colorize_table(resp.content, None),
               markdown.markdown(value)), match)


def filter_upload(value):
    pattern = re.compile('\[local (\S+) *\]', flags=re.IGNORECASE)

    match = re.search(pattern, value)
    if match is None:
        return value, None

    (file_type, encoding) = mimetypes.guess_type(
                                            os.path.join(MEDIA_ROOT, value))

    # FIXME: Can we trust the 'guessed' mimetype?
    if not file_type.startswith('text'):
        return (value, None)

    # FIXME: Limit to 1MB right now
    try:
        f = open(value)
    except IOError:
        return (value, None)

    text = f.read(1048576)
    f.close()

    text = _colorize_table(text, None)

    # FIXME: Assume all files are only intepreted for code, not markdown?
    return (text, True)
