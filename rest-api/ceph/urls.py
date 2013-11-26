from django.conf.urls import patterns, include, url
from rest_framework import routers
from ceph import views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'user', views.UserViewSet)
router.register(r'cluster', views.ClusterViewSet, base_name='cluster')


urlpatterns = patterns(
    '',
    url(r'^user/me', views.user_me),
    url(r'^', include(router.urls)),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/osd_map', views.OSDMap.as_view(), name='cluster-osd-map'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/health$', views.Health.as_view(), name='cluster-health'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/health_counters$', views.HealthCounters.as_view(),
        name='cluster-health-counters'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/space$', views.Space.as_view(), name='osd-space'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/osd$', views.OSDList.as_view(), name='cluster-osd-list'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/osd/(?P<osd_id>\d+)$', views.OSDDetail.as_view(),
        name='cluster-osd-detail'),

    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/request/(?P<request_id>[a-zA-Z0-9-]+)$',
        views.RequestViewSet.as_view({'get': 'retrieve'}), name='cluster-request-detail'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/request$',
        views.RequestViewSet.as_view({'get': 'list'}), name='cluster-request-list'),

    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/crush_rule_set$', views.CrushRuleSetViewSet.as_view({'get': 'list'}),
        name='cluster-crush_rule_set-list'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/crush_rule$', views.CrushRuleViewSet.as_view({'get': 'list'}),
        name='cluster-crush_rule-list'),

    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/pool$', views.PoolViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='cluster-pool-list'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/pool/(?P<pool_id>\d+)$', views.PoolViewSet.as_view({
        'get': 'retrieve',
        'patch': 'update'}),
        name='cluster-pool-detail'),
)
