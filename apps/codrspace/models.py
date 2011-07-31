import os
import re
import uuid
from django.db import models
from django.contrib.auth.models import User

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
    content = models.TextField()
    slug = models.SlugField(editable=False)
    author = models.ForeignKey(User, editable=False)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=0)
    publish_dt = models.DateTimeField(editable=False, null=True)
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)


class Media(models.Model):
    file = models.FileField(upload_to=file_directory, null=True)
    filename = models.CharField(max_length=200, editable=False)
    upload_dt = models.DateTimeField(auto_now_add=True)


class Profile(models.Model):
    git_access_token = models.CharField(max_length=75, null=True)
    user = models.OneToOneField(User)
    meta = models.TextField(null=True)


    def get_meta(self):
        from django.utils import simplejson
        return simplejson.loads(self.meta)
