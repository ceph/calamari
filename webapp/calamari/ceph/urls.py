from django.conf.urls import patterns, url
from rest_framework import routers
from ceph.views import UserViewSet, ClusterViewSet

router = routers.DefaultRouter()
router.register(r'user', UserViewSet)
router.register(r'cluster', ClusterViewSet)
urlpatterns = router.urls
