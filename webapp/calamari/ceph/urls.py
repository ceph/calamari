from django.conf.urls import patterns, url
from rest_framework import routers
from ceph.views import UserViewSet, ClusterViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'clusters', ClusterViewSet)
urlpatterns = router.urls
