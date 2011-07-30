from django.db import models
from django.contrib.auth.models import User


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
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)


class Profile(models.Model):
    git_access_token = models.CharField(max_length=75, null=True)
    user = models.OneToOneField(User)
