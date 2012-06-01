from django.conf.urls import patterns, include, url

urlpatterns = patterns('afterglow.views',
     url(r'^process$', 'processForm'),
     url(r'^$', 'index'),
)
