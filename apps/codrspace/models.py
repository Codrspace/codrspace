from django.db import models
<<<<<<< HEAD
=======

>>>>>>> e7a810eafd4e034099bbf4f0cfa4210b232d59bb

class CodrSpace(models.Model):
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)
