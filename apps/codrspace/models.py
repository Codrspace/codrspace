from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
