from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('codrspace.views',
    url(r'^$', 'index', name="home_base"),
    url(r'^add/$', 'add', name="add"),
    url(r'^edit/(?P<pk>\d+)/$', 'edit', name="edit"),
    url(r'^signin/$', 'signin_start', name="signin_start"),
    url(r'^signin_callback/$', 'signin_callback', name="signin_callback"),
    url(r'^signout/$', 'signout', name="signout"),
)

urlpatterns += patterns('codrspace.mock_views',
    url(r'^authorize/$', 'authorize', name="authorize"),
    url(r'^access_token/$', 'access_token', name="access_token"),
)
