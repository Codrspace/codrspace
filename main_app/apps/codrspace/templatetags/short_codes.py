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


def _add_slashes(value, reverse=False):
    """
    Add slashes to special sequences like newline
    and return so that markdown doesn't convert them
    """
    value = value.replace('\\n','\\\\n')
    value = value.replace('\\r','\\\\r')
    return value


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
            gist_text += '<hr><p class="github_convo">Join the conversation on ' + \
                            '<a href="%s#comments">github</a> (%d comments)</p>' % (
                                content['html_url'], content['comments'])

        gist_text = _add_slashes(gist_text)

        # Replace just first instance of the short code found
        value = re.sub(pattern, gist_text, markdown.markdown(value), count=1)

    return (value, True)


def filter_upload(value):
    pattern = re.compile('\[local (\S+) *\]', flags=re.IGNORECASE)

    files = re.findall(pattern, value)
    if not len(files):
        return value, None

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
        text += '<hr><br>'
        text = _add_slashes(text)

        value = re.sub(pattern, text, markdown.markdown(value), count=1)

    return (value, True)
