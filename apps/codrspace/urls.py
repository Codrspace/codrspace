from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('articles',                  
    url(r'^$', 'views.index', name="home_base"),
)