from django.conf.urls import patterns, include, url
from rest_framework import routers
from ceph import views

router = routers.DefaultRouter(trailing_slash=False)

# In v1, the /user list URL existed but only told you usernames
# In v2 it should include displaynames and email addresses too (TODO #7097)
router.register(r'user', views.UserViewSet)
# The cluster view exists in both v1 and v2
# In v1 the update time was given as both an ISO9601 time and a unix timestamp
# In v2 all times are given in ISO9601 only.
router.register(r'cluster', views.ClusterViewSet, base_name='cluster')

# The salt_key view is new in 2.0
router.register(r'salt_key', views.SaltKeyViewSet, base_name='salt_key')


# This is new in v2
router.register(r'server', views.ServerViewSet, base_name='server')

urlpatterns = patterns(
    '',
    # In v1, the user/me URL existed but did almost nothing, it only supported GET and told
    # you your current username.
    # In v2, the view gets filled out to return the displayname and email address to, and support
    # PUT/PATCH operations for users to change their passwords (TODO #7097)
    url(r'^user/me', views.user_me),
    url(r'^', include(router.urls)),

    # In v1, the Health view gave you the 'health' sync_object and the cluster update time
    # In v2, you can request the sync object by name with /sync_object and you can get the
    # cluster update time from /cluster/<id>
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/health$', views.Health.as_view(), name='cluster-health'),

    # In v1, the HealthCounters view /cluster/<id>/health_counters gave you a JSON object in its 'counters' attribute
    # In v2, you get that information by doing a derived object request for the 'health_counters' object, andyou
    # can get the cluster update time from /cluster/<id>
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/health_counters$', views.HealthCounters.as_view(),
        name='cluster-health-counters'),

    # In v1, the Space view /cluster/<id>/space gave you ceph.cluster.{}.df.[used_bytes|capacity_bytes|free_bytes]
    # In v2, you can get these directly using the TODO view that takes a tuple of stat names and gives you latest values
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/space$', views.Space.as_view(), name='osd-space'),

    # TODO what does this look like in v2 (remember frontend depends on filtering by pg state)
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/osd$', views.OSDList.as_view(), name='cluster-osd-list'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/osd/(?P<osd_id>\d+)$', views.OSDDetail.as_view(),
        name='cluster-osd-detail'),

    # This is new in v2
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/request/(?P<request_id>[a-zA-Z0-9-]+)$',
        views.RequestViewSet.as_view({'get': 'retrieve'}), name='cluster-request-detail'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/request$',
        views.RequestViewSet.as_view({'get': 'list'}), name='cluster-request-list'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/crush_rule_set$', views.CrushRuleSetViewSet.as_view({'get': 'list'}),
        name='cluster-crush_rule_set-list'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/crush_rule$', views.CrushRuleViewSet.as_view({'get': 'list'}),
        name='cluster-crush_rule-list'),
    # Unadulterated direct access to the maps that cthulhu syncs up from the mons
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/sync_object/(?P<sync_type>[a-zA-Z0-9-_]+)$',
        views.SyncObject.as_view(), name='cluster-sync-object'),
    # Unadulterated direct access to the maps that cthulhu syncs up from the mons
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/derived_object/(?P<derived_type>[a-zA-Z0-9-_]+)$',
        views.DerivedObject.as_view(), name='cluster-derived-object'),
    url(r'^server/(?P<fqdn>[a-zA-Z0-9-\.]+)/grains$', views.ServerViewSet.as_view({'get': 'retrieve_grains'})),

    # In v1, the /pool view gave you cluster,pool_id,name,quota_max_bytes,quota_max_objects,used_objects,used_bytes
    # In v2, you get more generally, but the used_* fields are gone, you use the (TODO) graphite latest value query
    # to get those.
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/pool$', views.PoolViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='cluster-pool-list'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/pool/(?P<pool_id>\d+)$', views.PoolViewSet.as_view({
        'get': 'retrieve',
        'patch': 'update'}),
        name='cluster-pool-detail'),


    # In v1 the server view gave you ('addr', 'hostname', 'name', 'services') and
    # each service gave you ('type', 'service_id', 'name').
    # In v2 all that and more is available, names are a little different and all
    # servers have a 'fqdn' and 'hostname' attribute.  Servers are uniquely
    # identified by FQDN.  In v2 there is also a /grains sub-url which
    # gives you all the salt grains
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/server$', views.ServerClusterViewSet.as_view({'get': 'list'}),
        name='cluster-server-list'),
    url(r'^cluster/(?P<fsid>[a-zA-Z0-9-]+)/server/(?P<fqdn>[a-zA-Z0-9-\.]+)$', views.ServerClusterViewSet.as_view({
        'get': 'retrieve'}),
        name='cluster-server-detail'),
)
