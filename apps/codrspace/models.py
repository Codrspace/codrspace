from django.db import models
from base.fields import SlugField

class CodrSpace(models.Model):
	slug = SlugField(unique=True)
	title = models.CharField(max_length=200, blank=True)
	content = models.TextField()
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)