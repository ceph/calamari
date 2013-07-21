from django.conf.urls import patterns, include, url
from rest_framework import routers
from ceph.views import UserViewSet, ClusterViewSet, OSDList, OSDDetail

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'user', UserViewSet)
router.register(r'cluster', ClusterViewSet)

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^cluster/(?P<cluster_pk>[0-9]+)/osd$', OSDList.as_view(), name='osd-list'),
    url(r'^cluster/(?P<cluster_pk>[0-9]+)/osd/(?P<osd_id>\d+)$', OSDDetail.as_view(), name='osd-detail'),
)
