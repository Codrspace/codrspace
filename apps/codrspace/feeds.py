from datetime import datetime
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from codrspace.models import Post


class LatestPostsFeed(Feed):
    description_template = 'feeds/post_description.html'

    def get_object(self, request, username):
        return get_object_or_404(User, username=username)

    def title(self, obj):
        return 'Codrspace: Posts by %s' % obj

    def link(self, obj):
        return '/%s/feed/' % obj

    def description(self, obj):
        return "Codrspace: All posts authored by %s" % obj

    def items(self, user):
        posts = Post.objects.filter(
            publish_dt__lte=datetime.now(),
            status='published',
            author=user,
        )
        return posts.order_by('-publish_dt')[:10]

    def item_title(self, item):
        return item.title or 'Untitled'

    def item_description(self, item):
        return item.content
