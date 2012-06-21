from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, \
        get_lexer_for_filename, \
        guess_lexer, \
        ClassNotFound
from codrspace.pygments.styles.github import GithubStyle

register = template.Library()


def _colorize_table(value, lang=None):
    return mark_safe(highlight(value, get_lexer(value, lang), HtmlFormatter(style=GithubStyle)))


def generate_pygments_css(path=None):
    if path is None:
        import os
        path = os.path.join(os.getcwd(), 'pygments.css')
    f = open(path, 'w')
    f.write(HtmlFormatter(style=GithubStyle).get_style_defs('.highlight'))
    f.close()


def get_lexer(value, lang):
    if lang:
        if '.' in lang:
            return get_lexer_for_filename(lang)  # possibly a filename, poor detection for now
        else:
            return get_lexer_by_name(lang)  # guess it by specific language
    # try and guess the lexer by content
    return guess_lexer(value)


@register.filter(name='colorize')
@stringfilter
def colorize(value, arg=None):
    try:
        return mark_safe(highlight(value, get_lexer(value, arg), HtmlFormatter(style=GithubStyle)))
    except ClassNotFound:
        return value


@register.filter(name='colorize_table')
@stringfilter
def colorize_table(value, arg=None):
    try:
        return _colorize_table(value, arg)
    except ClassNotFound:
        return value
