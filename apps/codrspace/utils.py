from timezones.utils import adjust_datetime_to_timezone
from bs4 import BeautifulSoup, Comment

from django.conf import settings


def localize_date(date, from_tz=None, to_tz=None):
    """
    Convert from one timezone to another
    """
    # set the defaults
    if from_tz is None:
        from_tz = settings.TIME_ZONE

    if to_tz is None:
        to_tz = "US/Central"

    date = adjust_datetime_to_timezone(date, from_tz=from_tz, to_tz=to_tz)
    date = date.replace(tzinfo=None)
    return date


def clean_html(html):
    """Use beautifulsoup4 to clean html"""
    allowed_tags = ['p', 'br', 'span', 'small']
    allowed_attributes = []

    soup = BeautifulSoup(html, "html.parser")

    # strip unwanted tags an attribute
    for tag in soup.findAll():
        if tag.name.lower() not in allowed_tags:
            tag.extract()
            continue

        for attr in tag.attrs.keys():
            if attr not in allowed_attributes:
                del tag.attrs[attr]

    # scripts can be executed from comments in some cases
    comments = soup.findAll(text=lambda text: isinstance(text, Comment))
    for comment in comments:
        comment.extract()

    return unicode(soup)


def apply_class(html, element, _class):
    """Apply a class to a all elements of type element"""
    soup = BeautifulSoup(html, "html.parser")

    # strip unwanted tags an attribute
    for tag in soup.findAll(element):
        tag.attrs['class'] = _class

    return unicode(soup)
