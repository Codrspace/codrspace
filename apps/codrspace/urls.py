from django.conf.urls.defaults import patterns, url, include
from codrspace.feeds import LatestPostsFeed
from codrspace.api import PostResource


post_resource = PostResource()

urlpatterns = patterns('codrspace.views',
    url(r'^$', 'index', name="homepage"),
    url(r'^admin/add/$', 'add', name="add"),
    url(r'^admin/edit/(?P<pk>\d+)/$', 'edit', name="edit"),
    url(r'^admin/delete/(?P<pk>\d+)/$', 'delete', name="delete"),
    url(r'^settings/$', 'user_settings', name="user_settings"),
    url(r'^api-settings/', 'api_settings', name="api_settings"),
    url(r'^signin/$', 'signin_start', name="signin_start"),
    url(r'^signin_callback/$', 'signin_callback', name="signin_callback"),
    url(r'^signout/$', 'signout', name="signout"),
    url(r'^feedback/$', 'feedback', name="feedback"),
    url(r'^api/', include(post_resource.urls)),
)

urlpatterns += patterns('codrspace.mock_views',
    url(r'^fake_user/$', 'fake_user', name="fake_user"),
    url(r'^authorize/$', 'authorize', name="authorize"),
    url(r'^access_token/$', 'access_token', name="access_token"),
)

urlpatterns += patterns('codrspace.views',
    url(r'^(?P<username>[\w\d\-\.]+)/feed/$', LatestPostsFeed(), name="posts_feed"),
    url(r'^(?P<username>[\w\d\-\.]+)/(?P<slug>[\w\d\-]+)/$', 'post_detail',
        name="post_detail"),
    url(r'^(?P<username>[\w\d\-\.]+)/$', 'post_list', name="post_list"),
)
