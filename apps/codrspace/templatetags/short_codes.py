"""Custom filters to grab code from the web via short codes"""

import requests
import mimetypes
import re
import os
import markdown
import HTMLParser
from hashlib import md5

from django.utils import simplejson
from django import template
from django.utils.safestring import mark_safe
from settings import MEDIA_ROOT

from codrspace.templatetags.syntax_color import _colorize_table
from codrspace.utils import clean_html, apply_class
from codrspace.pygments.over_pygments import add_colors_to


register = template.Library()
html_parser = HTMLParser.HTMLParser()


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
    all_replacements = []

    # get the replacement values and content with replacement hashes
    for name, var in vars(module).items():
        if type(var) == types.FunctionType and name.startswith('filter_'):
            replacements, value, match = var(value)
            if match:
                all_replacements.extend(replacements)

    # clean the html before it goes into markdown processing
    # and while it has hash values
    value = clean_html(value)

    # this is a quick fix, but html.parser with beautiful soup
    # converts some symbols to the html entity here we convert them back
    # so things like blockquotes work
    value = html_parser.unescape(value)

    # convert to markdown
    value = markdown.markdown(value, ['tables'])

    # apply classes that are needed for certain bootstrap styling
    value = apply_class(value, 'table', 'table')

    # replace the hash values with the replacement values
    for r in all_replacements:
        _hash, text = r
        value = value.replace(_hash, text)

    return mark_safe(value)


def filter_gitstyle(value):
    replacements = []
    pattern = re.compile("```(?P<lang>[^\\n\\s`]+)+?(?P<code>[^```]+)+?```", re.I | re.S | re.M)

    if len(re.findall(pattern, value)) == 0:
        return (replacements, value, None,)

    git_styles = re.finditer(pattern, value)

    for gs in git_styles:
        try:
            lang = gs.group('lang')
        except IndexError:
            lang = None

        text = _colorize_table(gs.group('code'), lang=lang)
        text_hash = md5(text.encode('utf-8')).hexdigest()

        replacements.append([text_hash, text])
        value = re.sub(pattern, text_hash, value, count=1)

    return (replacements, value, True,)


def filter_inline(value):
    replacements = []
    pattern = re.compile('\\[code(\\s+lang=\"(?P<lang>[\\w]+)\")*\\s*' + \
                        '(?P<more_colors>more_colors)*\\](?P<code>.*?)\\[/code\\]', 
                        re.I | re.S | re.M)

    if len(re.findall(pattern, value)) == 0:
        return (replacements, value, None,)

    inlines = re.finditer(pattern, value)

    for inline_code in inlines:
        try:
            lang = inline_code.group('lang')
        except IndexError:
            lang = None

        try:
            more_colors = (inline_code.group('more_colors') == 'more_colors')
        except IndexError:
            more_colors = False

        text = _colorize_table(inline_code.group('code'), lang=lang)

        # per-word coloring for user defined names
        if more_colors:
            text = add_colors_to(text)

        text_hash = md5(text.encode('utf-8')).hexdigest()

        replacements.append([text_hash, text])
        value = re.sub(pattern, text_hash, value, count=1)

    return (replacements, value, True,)


def filter_gist(value):
    gist_base_url = 'https://api.github.com/gists/'
    replacements = []
    pattern = re.compile('\[gist ([a-f0-9]+) *\]', flags=re.IGNORECASE)

    ids = re.findall(pattern, value)
    if not len(ids):
        return (replacements, value, None,)

    for gist_id in ids:
        gist_text = ""
        lang = None
        resp = requests.get('%s%s' % (gist_base_url, gist_id))

        if resp.status_code != 200:
            return (replacements, value, None,)

        content = simplejson.loads(resp.content)

        # Go through all files in gist and smash 'em together
        for name in content['files']:
            _file = content['files'][name]

            # try and get the language of the file either
            # by passing filename or by passing the language
            # specified
            if 'filename' in _file:
                lang = _file['filename']
            elif 'language' in _file:
                lang= _file['language']

            gist_text += "%s" % (
                _colorize_table(_file['content'], lang=lang))

        if content['comments'] > 0:
            gist_text += '<hr><p class="github_convo">Join the conversation on ' + \
                            '<a href="%s#comments">github</a> (%d comments)</p>' % (
                                content['html_url'], content['comments'])

        text_hash = md5(gist_text.encode('utf-8')).hexdigest()

        replacements.append([text_hash, gist_text])
        value = re.sub(pattern, text_hash, value, count=1)

    return (replacements, value, True,)


def filter_upload(value):
    replacements = []
    pattern = re.compile('\[local (\S+) *\]', flags=re.IGNORECASE)

    files = re.findall(pattern, value)
    if not len(files):
        return (replacements, value, None,)

    for file_name in files:
        colorize = True
        file_path = os.path.join(MEDIA_ROOT, file_name)
        (file_type, encoding) = mimetypes.guess_type(file_path)

        if file_type is None:
            colorize = False

        # FIXME: Can we trust the 'guessed' mimetype?
        if file_type in ['application', 'text']:
            colorize = False

        # FIXME: Limit to 1MB right now
        try:
            f = open(file_path)
            text = f.read(1048576)
            f.close()
        except IOError:
            colorize = False

        if colorize:
            text = _colorize_table(text, lang=file_name)
            text_hash = md5(text.encode('utf-8')).hexdigest()
        else:
            text = '[local %s]' % file_name
            text_hash = md5(text.encode('utf-8')).hexdigest()

        replacements.append([text_hash, text])
        value = re.sub(pattern, text_hash, value, count=1)

    return (replacements, value, True,)
