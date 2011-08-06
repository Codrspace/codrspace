import os
import re
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.utils.hashcompat import md5_constructor
from django.core.cache import cache
from django.utils.http import urlquote


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
    slug = models.SlugField(unique=True, editable=False)
    author = models.ForeignKey(User, editable=False)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=0)
    publish_dt = models.DateTimeField(editable=False, null=True)
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        # slug via title
        slug = slugify(self.title)
        self.slug = slug

        # if no slug aka via no title
        if not self.slug:
            self.slug = Post.objects.count() + 1

        # if slug exists
        count = 1
        while True:

            if self.pk:
                slug_exists = Post.objects.filter(
                    slug=self.slug).exclude(
                    pk=self.pk).exists()
            else:
                slug_exists = Post.objects.filter(
                    slug=self.slug).exists()

            if slug_exists:
                count += 1
                self.slug = '%s-%d' % (slug, count)
            else:
                break

        super(Post, self).save(*args, **kwargs)

        # Invalidate cache for all individual posts and the list of posts
        invalidate_cache_key('content', self.pk)
        invalidate_cache_key('post_list', self.author.pk)

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
            'code': ('.txt', '.py', '.htm', '.html', '.css', '.js', '.rb'),
        }

        for type in types:
            if ext in types[type]:
                return type

        return ''

    def shortcode(self):
        shortcode = ''

        if self.type() == 'image':
            shortcode = "![%s](%s)" % (self.filename, self.file.url)

        if self.type() == 'code':
            shortcode = "[local %s]" % self.file.name

        return shortcode


class Profile(models.Model):
    git_access_token = models.CharField(max_length=75, null=True)
    user = models.OneToOneField(User)
    meta = models.TextField(null=True)

    def get_meta(self):
        from django.utils import simplejson
        return simplejson.loads(self.meta)
