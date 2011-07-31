"""Custom filters to grab code from the web via short codes"""


import requests
import re

from django.utils import simplejson
from django import template
from django.utils.safestring import mark_safe
from codrspace.templatetags.syntax_color import _colorize_table
import markdown
register = template.Library()


@register.filter(name='explosivo')
def explosivo(value, lang):
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
            value = var(value, lang)

    return mark_safe(value)


def filter_gist(value, lang):
    pattern = re.compile('\[gist (\d+) *\]', flags=re.IGNORECASE)

    match = re.search(pattern, value)
    if match is None:
        return value

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

    return re.sub(pattern, gist_text, markdown.markdown(value))


def filter_url(value, lang):
    pattern = re.compile('\[url (\S+) *\]', flags=re.IGNORECASE)

    match = re.search(pattern, value)
    if match is None:
        return value

    url = match.group(1)

    # FIXME: Validate that value is actually a url
    resp = requests.get(url)

    if resp.status_code != 200:
        return value

    return re.sub(pattern, _colorize_table(resp.content, None), markdown.markdown(value))


def filter_upload(value, lang):
    return value

if __name__ == "__main__":
    explosivo('test')
