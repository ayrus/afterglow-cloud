from django.conf.urls import patterns, include, url

urlpatterns = patterns('afterglow_cloud.app.views',
     url(r'^process$', 'processForm'),
     url(r'^$', 'index'),
     url(r'^contact$', 'contact'),
)
