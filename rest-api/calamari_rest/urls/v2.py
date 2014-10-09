
from django.conf.urls import patterns, url, include
from rest_framework import routers
import calamari_rest.views.v1
import calamari_rest.views.v2

router = routers.DefaultRouter(trailing_slash=False)

# Presentation of django.contrib.auth.models.User
router.register(r'user', calamari_rest.views.v1.UserViewSet)

# Information about each Ceph cluster (FSID), see sub-URLs
router.register(r'cluster', calamari_rest.views.v2.ClusterViewSet, base_name='cluster')

urlpatterns = patterns(
    '',

    # About the host calamari server is running on
    url(r'^grains', calamari_rest.views.v2.grains),
    url(r'^info', calamari_rest.views.v1.Info.as_view()),

    # Wrapping django auth
    url(r'^auth/login', calamari_rest.views.v1.login),
    url(r'^auth/logout', calamari_rest.views.v1.logout),

    # This has to come after /user/me to make sure that special case is handled
    url(r'^', include(router.urls)),

    # About ongoing operations in cthulhu
    url(r'^request/(?P<request_id>[a-zA-Z0-9-]+)/cancel$',
        calamari_rest.views.v2.RequestViewSet.as_view({'post': 'cancel'}),
        name='request-cancel'),
    url(r'^request/(?P<request_id>[a-zA-Z0-9-]+)$',
        calamari_rest.views.v2.RequestViewSet.as_view({'get': 'retrieve'}),
        name='request-detail'),
    url(r'^request$',
        calamari_rest.views.v2.RequestViewSet.as_view({'get': 'list'}),
        name='request-list'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/request/(?P<request_id>[a-zA-Z0-9-]+)$',
        calamari_rest.views.v2.RequestViewSet.as_view({'get': 'retrieve'}),
        name='cluster-request-detail'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/request$',
        calamari_rest.views.v2.RequestViewSet.as_view({'get': 'list'}),
        name='cluster-request-list'),

    # OSDs, Pools, CRUSH
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/crush_map$',
        calamari_rest.views.v2.CrushMapViewSet.as_view({'get': 'retrieve', 'post': 'replace'}),
        name='cluster-crush_map'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/crush_rule_set$',
        calamari_rest.views.v2.CrushRuleSetViewSet.as_view({'get': 'list'}),
        name='cluster-crush_rule_set-list'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/crush_rule$',
        calamari_rest.views.v2.CrushRuleViewSet.as_view({'get': 'list'}),
        name='cluster-crush_rule-list'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/crush_node$',
        calamari_rest.views.v2.CrushNodeViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='cluster-crush_node-list'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/crush_node/(?P<node_id>-*\d+)$',
        calamari_rest.views.v2.CrushNodeViewSet.as_view({'get': 'retrieve', 'patch': 'update', 'delete': 'destroy'}),
        name='cluster-crush_node-detail'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/pool$',
        calamari_rest.views.v2.PoolViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='cluster-pool-list'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/pool/(?P<pool_id>\d+)$',
        calamari_rest.views.v2.PoolViewSet.as_view({'get': 'retrieve',
                                                    'patch': 'update',
                                                    'delete': 'destroy'}),
        name='cluster-pool-detail'),

    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/osd$',
        calamari_rest.views.v2.OsdViewSet.as_view({'get': 'list'}),
        name='cluster-osd-list'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/osd/(?P<osd_id>\d+)$',
        calamari_rest.views.v2.OsdViewSet.as_view({'get': 'retrieve', 'patch': 'update'}),
        name='cluster-osd-detail'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/osd /command$',
        calamari_rest.views.v2.OsdViewSet.as_view({'get': 'get_implemented_commands'})),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/osd/(?P<osd_id>\d+)/command$',
        calamari_rest.views.v2.OsdViewSet.as_view({'get': 'get_valid_commands'})),

    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/osd/(?P<osd_id>\d+)/command/(?P<command>[a-zA-Z_]+)$',
        calamari_rest.views.v2.OsdViewSet.as_view({'get': 'validate_command', 'post': 'apply'})),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/osd_config$',
        calamari_rest.views.v2.OsdConfigViewSet.as_view({'get': 'osd_config', 'patch': 'update'})),

    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/mon$',
        calamari_rest.views.v2.MonViewSet.as_view({'get': 'list'}),
        name='cluster-mon-list'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/mon/(?P<mon_id>[a-zA-Z0-9-\.]+)$',
        calamari_rest.views.v2.MonViewSet.as_view({'get': 'retrieve'}),
        name='cluster-mon-detail'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/mon/(?P<mon_id>[a-zA-Z0-9-\.]+)/status$',
        calamari_rest.views.v2.MonViewSet.as_view({'get': 'retrieve_status'}),
        name='cluster-mon-detail-status'),

    # Direct access to SyncObjects, mainly for debugging
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/sync_object$',
        calamari_rest.views.v2.SyncObject.as_view({'get': 'describe'}),
        name='cluster-sync-object-describe'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/sync_object/(?P<sync_type>[a-zA-Z0-9-_]+)$',
        calamari_rest.views.v2.SyncObject.as_view({'get': 'retrieve'}),
        name='cluster-sync-object'),
    url(r'^server/(?P<fqdn>[a-zA-Z0-9-\.]+)/debug_job',
        calamari_rest.views.v2.DebugJob.as_view({'post': 'create'}),
        name='server-debug-job'),

    # All about servers
    url(r'^key$', calamari_rest.views.v2.SaltKeyViewSet.as_view(
        {'get': 'list', 'patch': 'list_partial_update', 'delete': 'list_destroy'})),
    url(r'^key/(?P<minion_id>[a-zA-Z0-9-\.]+)',
        calamari_rest.views.v2.SaltKeyViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})),

    url(r'^server$',
        calamari_rest.views.v2.ServerViewSet.as_view({'get': 'list'})),
    url(r'^server/(?P<fqdn>[a-zA-Z0-9-\.]+)$',
        calamari_rest.views.v2.ServerViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'})),
    url(r'^server/(?P<fqdn>[a-zA-Z0-9-\.]+)/grains$',
        calamari_rest.views.v2.ServerViewSet.as_view({'get': 'retrieve_grains'})),

    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/server$',
        calamari_rest.views.v2.ServerClusterViewSet.as_view({'get': 'list'}),
        name='cluster-server-list'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/server/(?P<fqdn>[a-zA-Z0-9-\.]+)$',
        calamari_rest.views.v2.ServerClusterViewSet.as_view({'get': 'retrieve'}),
        name='cluster-server-detail'),

    # Ceph configuration settings
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/config$',
        calamari_rest.views.v2.ConfigViewSet.as_view({'get': 'list'})),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/config/(?P<key>[a-zA-Z0-9_]+)$',
        calamari_rest.views.v2.ConfigViewSet.as_view({'get': 'retrieve'})),

    # Events
    url(r'^event$',
        calamari_rest.views.v2.EventViewSet.as_view({'get': 'list'})),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/event$',
        calamari_rest.views.v2.EventViewSet.as_view({'get': 'list_cluster'})),
    url(r'^server/(?P<fqdn>[a-zA-Z0-9-\.]+)/event$',
        calamari_rest.views.v2.EventViewSet.as_view({'get': 'list_server'})),

    # Log tail
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/log$',
        calamari_rest.views.v2.LogTailViewSet.as_view({'get': 'get_cluster_log'})),
    url(r'^server/(?P<fqdn>[a-zA-Z0-9-\.]+)/log$',
        calamari_rest.views.v2.LogTailViewSet.as_view({'get': 'list_server_logs'})),
    url(r'^server/(?P<fqdn>[a-zA-Z0-9-\.]+)/log/(?P<log_path>.+)$',
        calamari_rest.views.v2.LogTailViewSet.as_view({'get': 'get_server_log'})),

    # Ceph CLI access
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/cli$',
        calamari_rest.views.v2.CliViewSet.as_view({'post': 'create'}))
)
