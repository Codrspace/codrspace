from django.contrib.sitemaps import Sitemap
from django.contrib.auth.models import User
from django.conf import settings
from codrspace.models import Post


class DefaultMap(Sitemap):
    def items(self):
        return [
            '/',
            '/signin/'
        ]

    def location(self, obj):
        return obj

    def priority(self, obj):
        return '0.7'


class UserMap(Sitemap):
    def items(self):
        return User.objects.all()

    def location(self, obj):
        return '/%s/' % obj.username

    def priority(self, obj):
        return '0.5'


class PostMap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return Post.objects.filter(status='published').order_by("-publish_dt")

    def lastmod(self, obj):
        return obj.update_dt
