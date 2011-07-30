"""Custom filters to grab code from the web via short codes"""


import requests
import re

from django.utils import simplejson
from django import template

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
            value = var(value)

    return value


def filter_gist(value):
    # FIXME: Make case insensitive
    pattern = re.compile('\[gist (\d+)\]')

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
        gist_text += "file: %s content: %s<br>" % (
                                    name, content['files'][name]['content'])

    return re.sub(pattern, gist_text, value)


def filter_url(value):
    return value


def filter_upload(value):
    return value

if __name__ == "__main__":
    explosivo('test')
