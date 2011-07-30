from django.db import models


class Profile(models.Model):
	git_access_token = models.CharField(max_length=75)
