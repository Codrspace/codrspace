import os
import re
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils.hashcompat import md5_constructor
from django.core.cache import cache
from django.utils.http import urlquote
from django.conf import settings
from timezones.fields import TimeZoneField
from tastypie.models import create_api_key
from codrspace.managers import SettingManager

models.signals.post_save.connect(create_api_key, sender=User)


def invalidate_cache_key(fragment_name, *variables):
    args = md5_constructor(u':'.join([urlquote(var) for var in variables]))
    cache_key = 'template.cache.%s.%s' % (fragment_name, args.hexdigest())
    cache.delete(cache_key)


def file_directory(instance, filename):
    filename = re.sub(r'[^a-zA-Z0-9._]+', '-', filename)
    filename, ext = os.path.splitext(filename)
    return '%s%s' % (uuid.uuid1().hex[:13], ext)


class Post(models.Model):

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    title = models.CharField(max_length=200, blank=True)
    content = models.TextField(blank=True)
    slug = models.SlugField(max_length=75)
    author = models.ForeignKey(User, editable=False)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=0)
    publish_dt = models.DateTimeField(null=True)
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("slug", "author")

    def __unicode__(self):
        return '%s' % (self.title or 'Untitled')

    def url(self):
        return '%s%s' % (settings.SITE_URL, self.get_absolute_url(),)

    def save(self, *args, **kwargs):
        super(Post, self).save(*args, **kwargs)

        # Invalidate cache for all individual posts and the list of posts
        invalidate_cache_key('content', self.pk)

    @models.permalink
    def get_absolute_url(self):
        return ("post_detail", [self.author.username, self.slug])


class Media(models.Model):
    file = models.FileField(upload_to=file_directory, null=True)
    filename = models.CharField(max_length=200, editable=False)
    uploader = models.ForeignKey(User, editable=False)
    upload_dt = models.DateTimeField(auto_now_add=True)

    def type(self):
        ext = os.path.splitext(self.filename)[1].lower()
        # map file-type to extension
        types = {
            'image': ('.jpg', '.jpeg', '.gif', '.png', '.tif', '.tiff',
                      '.bmp',),
            'text': ('.txt', '.doc', '.docx'),
            'spreadsheet': ('.csv', '.xls', '.xlsx'),
            'powerpoint': ('.ppt', '.pptx'),
            'pdf': ('.pdf'),
            'video': ('.wmv', '.mov', '.mpg', '.mp4', '.m4v'),
            'zip': ('.zip'),
            'code': ('.txt', '.py', '.htm', '.html', '.css', '.js', '.rb', '.sh'),
        }

        for type in types:
            if ext in types[type]:
                return type

        return 'code'

    def shortcode(self):
        shortcode = ''

        if self.type() == 'image':
            shortcode = "![%s](%s)" % (self.filename, self.file.url)

        if self.type() == 'code':
            shortcode = "[local %s]" % self.file.name

        return shortcode


class Setting(models.Model):
    """
    Settings model for specific blog settings
    """
    blog_title = models.CharField(max_length=75, null=True, blank=True)
    blog_tagline = models.CharField(max_length=150, null=True, blank=True)
    name = models.CharField(max_length=30, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, editable=False)
    timezone = TimeZoneField(default="US/Central")

    objects = SettingManager()


class Profile(models.Model):
    git_access_token = models.CharField(max_length=75, null=True)
    user = models.OneToOneField(User)
    meta = models.TextField(null=True)

    def get_meta(self):
        from django.utils import simplejson
        return simplejson.loads(self.meta)
