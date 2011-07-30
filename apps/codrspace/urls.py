from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('codrspace.views',
    url(r'^$', 'index', name="home_base"),
    url(r'^edit/$', 'edit', name="edit"),
    url(r'^signin/$', 'signin_start', name="signin_start"),
    url(r'^signin_callback/$', 'signin_callback', name="signin_callback"),
)
