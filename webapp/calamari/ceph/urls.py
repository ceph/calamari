from django.conf.urls import patterns, include, url
from rest_framework import routers
from ceph import views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'user', views.UserViewSet)
router.register(r'cluster', views.ClusterViewSet)

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^cluster/(?P<cluster_pk>[0-9]+)/osd$', views.OSDList.as_view(), name='osd-list'),
    url(r'^cluster/(?P<cluster_pk>[0-9]+)/osd/(?P<osd_id>\d+)$', views.OSDDetail.as_view(), name='osd-detail'),
    url(r'^cluster/(?P<cluster_pk>[0-9]+)/osd/epoch/(?P<epoch>\d+)$', views.OSDListDelta.as_view(), name='osd-list-delta'),
)
