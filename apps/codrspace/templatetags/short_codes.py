"""Custom filters to grab code from the web via short codes"""


import requests
import mimetypes
import re
import os
import markdown
import urlparse

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
    import sys
    import types
    module = sys.modules[__name__]

    for name, var in vars(module).items():
        if type(var) == types.FunctionType and name.startswith('filter_'):
            value, match = var(value)
            if not match:
                value = markdown.markdown(value)

    return mark_safe(value)


def filter_gist(value):
    pattern = re.compile('\[gist (\d+) *\]', flags=re.IGNORECASE)

    ids = re.findall(pattern, value)
    if not len(ids):
        return value, None

    for gist_id in ids:
        gist_text = ""
        resp = requests.get('https://api.github.com/gists/%d' % (
                                                                int(gist_id)))

        if resp.status_code != 200:
            return value

        content = simplejson.loads(resp.content)

        # Go through all files in gist and smash 'em together
        for name in content['files']:
            gist_text += "%s" % (
                _colorize_table(content['files'][name]['content'], None))

        if content['comments'] > 0:
            gist_text += '<hr>Join the conversation on ' + \
                            '<a href="%s#comments">github</a> (%d comments)' % (
                                content['html_url'], content['comments'])

        # Replace just first instance of the short code found
        value = re.sub(pattern, gist_text, markdown.markdown(value), count=1)

    return (value, True)


def _validate_url(url):
    """Validate a url, return None if not value or url if valid"""
    parsed_url = urlparse.urlparse(url)

    if parsed_url.scheme != 'http' and parsed_url.scheme != 'https':
        return None

    if parsed_url.netloc == '':
        return None

    return url


def filter_url(value):
    pattern = re.compile('\[url (\S+) *\]', flags=re.IGNORECASE)

    urls = re.findall(pattern, value)
    if not len(urls):
        return (value, None)

    for url in urls:
        url = _validate_url(url)
        if url is None:
            return (value, None)

        # Validate that value is actually a url
        resp = requests.get(url)

        if resp.status_code != 200:
            return (value, None)

        value = re.sub(pattern, _colorize_table(resp.content, None),
                                                    markdown.markdown(value),
                                                    count=1)

    return (value, True)


def filter_upload(value):
    pattern = re.compile('\[local (\S+) *\]', flags=re.IGNORECASE)

    files = re.findall(pattern, value)
    if not len(files):
        return value, None

    # Smashed together text for all files
    full_text = ""

    for file_path in files:
        file_path = os.path.join(MEDIA_ROOT, file_path)
        (file_type, encoding) = mimetypes.guess_type(file_path)

        if file_type is None:
            return (value, None)

        # FIXME: Can we trust the 'guessed' mimetype?
        if not file_type.startswith('text'):
            return (value, None)

        # FIXME: Limit to 1MB right now
        try:
            f = open(file_path)
        except IOError:
            return (value, None)

        text = f.read(1048576)
        f.close()

        text = _colorize_table(text, None)

        # FIXME: Assume all files are only intepreted for code, not markdown?
        full_text += '%s<hr><br>' % (text)

    return (full_text, True)
