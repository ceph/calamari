
from django.conf.urls import patterns, url, include
from rest_framework import routers
from ceph import views

router = routers.DefaultRouter(trailing_slash=False)

# Presentation of django.contrib.auth.models.User
router.register(r'user', views.UserViewSet)

# Information about each Ceph cluster (FSID), see sub-URLs
router.register(r'cluster', views.ClusterViewSet, base_name='cluster')

# Server authentication keys, whether accepted or not
router.register(r'key', views.SaltKeyViewSet, base_name='key')

# Information about authenticated servers
router.register(r'server', views.ServerViewSet, base_name='server')


urlpatterns = patterns(
    '',

    # About the host calamari server is running on
    url(r'^grains', views.grains),
    url(r'^info', views.info),

    # Wrapping django auth
    url(r'^user/me', views.user_me),
    url(r'^auth/login', views.login),
    url(r'^auth/logout', views.logout),

    # This has to come after /user/me to make sure that special case is handled
    url(r'^', include(router.urls)),

    # About ongoing operations in cthulhu
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/request/(?P<request_id>[a-zA-Z0-9-]+)$',
        views.RequestViewSet.as_view({'get': 'retrieve'}), name='cluster-request-detail'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/request$',
        views.RequestViewSet.as_view({'get': 'list'}), name='cluster-request-list'),

    # OSDs, Pools, CRUSH
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
    # FIXME: the OSD stuff based on derived objects is a bit shonky
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/osd$', views.OSDList.as_view(), name='cluster-osd-list'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/osd/(?P<osd_id>\d+)$', views.OSDDetail.as_view(),
        name='cluster-osd-detail'),

    # Direct access to SyncObjects, DerivedObjects, graphite stats
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/sync_object/(?P<sync_type>[a-zA-Z0-9-_]+)$',
        views.SyncObject.as_view(), name='cluster-sync-object'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/derived_object/(?P<derived_type>[a-zA-Z0-9-_]+)$',
        views.DerivedObject.as_view(), name='cluster-derived-object'),

    # All about servers
    url(r'^server/(?P<fqdn>[a-zA-Z0-9-\.]+)/grains$', views.ServerViewSet.as_view({'get': 'retrieve_grains'})),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/server$', views.ServerClusterViewSet.as_view({'get': 'list'}),
        name='cluster-server-list'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/server/(?P<fqdn>[a-zA-Z0-9-\.]+)$', views.ServerClusterViewSet.as_view({
        'get': 'retrieve'}),
        name='cluster-server-detail'),





)
