from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('codrspace',
    url(r'^$', 'views.index', name="home_base"),
    url(r'^signin/$', 'views.signin_start', name="signin_start"),
    url(r'^signin_callback/$', 'views.signin_callback',
        name="signin_callback"),
)
