from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from ceph import views

urlpatterns = patterns('',
    url(r'^clusters/$', views.ClusterList.as_view()),
    url(r'^clusters/(?P<pk>[0-9]+)/$', views.ClusterDetail.as_view()),
)

urlpatterns = format_suffix_patterns(urlpatterns)
