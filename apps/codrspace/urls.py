from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('codrspace',        
    url(r'^$', 'views.index', name="home_base"),
)
