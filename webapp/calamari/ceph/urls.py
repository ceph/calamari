from django.conf.urls import patterns, url
from rest_framework import routers
from ceph.views import ClusterViewSet

router = routers.DefaultRouter()
router.register(r'clusters', ClusterViewSet)
urlpatterns = router.urls
