
from django.contrib.auth.models import User
from django.utils import dateformat

from rest_framework import serializers
from ceph.models import Cluster
import dateutil.parser


def to_unix(t):
    if t is None:
        return None
    return int(dateformat.format(t, 'U')) * 1000


class ClusterSerializer(serializers.Serializer):
    class Meta:
        fields = ('update_time', 'update_time_unix', 'id', 'name')

    update_time = serializers.Field()
    name = serializers.Field()
    id = serializers.Field()

    # FIXME: we should not be sending out time in two formats: if API consumers want
    # unix timestamps they can do the conversion themselves.
    update_time_unix = serializers.SerializerMethodField('get_update_time_unix')

    def get_update_time_unix(self, obj):
        update_time = dateutil.parser.parse(obj.update_time)
        return to_unix(update_time)

    # NB calamari 1.0 had cluster_atttempt_time, which no longer makes sense
    # because we're listening for events, not polling.  TODO: expunge from GUI code.


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the Django User model.

    Used to expose a django-rest-framework user management resource.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'password')

    def to_native(self, obj):
        # Before conversion, remove the password field. This prevents the hash
        # from being displayed when requesting user details.
        if 'password' in self.fields:
            del self.fields['password']
        return super(UserSerializer, self).to_native(obj)

    def restore_object(self, attrs, instance=None):
        user = super(UserSerializer, self).restore_object(attrs, instance)
        if user:
            # This will perform the Django-specific password obfuscation
            user.set_password(attrs['password'])
        return user


class ClusterSpaceSerializer(serializers.Serializer):
    space = serializers.Field()

    class Meta:
        model = Cluster
        fields = ('space',)


class ClusterHealthSerializer(serializers.Serializer):
    report = serializers.Field()

    class Meta:
        model = Cluster
        fields = ('report', 'cluster_update_time', 'cluster_update_time_unix')

    # FIXME: should not be copying this field onto health counters etc, clients should get
    # it by querying the cluster directly.
    cluster_update_time = serializers.Field()
    cluster_update_time_unix = serializers.SerializerMethodField('get_cluster_update_time_unix')

    def get_cluster_update_time_unix(self, obj):
        update_time = dateutil.parser.parse(obj.cluster_update_time)
        return to_unix(update_time)


class ClusterHealthCountersSerializer(serializers.ModelSerializer):
    pg = serializers.SerializerMethodField('get_pg')
    mds = serializers.SerializerMethodField('get_mds')
    mon = serializers.SerializerMethodField('get_mon')
    osd = serializers.SerializerMethodField('get_osd')

    class Meta:
        model = Cluster
        fields = ('pg', 'mds', 'mon', 'osd', 'cluster_update_time', 'cluster_update_time_unix')

    def get_pg(self, obj):
        return obj.counters['pg']

    def get_mds(self, obj):
        return obj.counters['mds']

    def get_mon(self, obj):
        return obj.counters['mon']

    def get_osd(self, obj):
        return obj.counters['osd']

    # FIXME: should not be copying this field onto health counters etc, clients should get
    # it by querying the cluster directly.
    cluster_update_time = serializers.Field()
    cluster_update_time_unix = serializers.SerializerMethodField('get_cluster_update_time_unix')

    def get_cluster_update_time_unix(self, obj):
        update_time = dateutil.parser.parse(obj.cluster_update_time)
        return to_unix(update_time)


class OSDDetailSerializer(serializers.Serializer):
    class Meta:
        # FIXME: should just be returning the OSD as the object
        fields = ('osd',)

    osd = serializers.Field()


class OSDListSerializer(serializers.Serializer):
    # TODO: the OSD list resource should just return a list, so that
    # this serializer class isn't necessary
    osds = serializers.Field()
    pg_state_counts = serializers.SerializerMethodField('get_pg_state_counts')

    def get_pg_state_counts(self, obj):
        return dict((s, len(v)) for s, v in obj.osds_by_pg_state.iteritems())

    class Meta:
        fields = ('osds', 'pg_state_counts')


class OSDMapSerializer(serializers.Serializer):
    class Meta:
        fields = ('version', 'data')

    version = serializers.IntegerField()
    data = serializers.Field()


class PoolSerializer(serializers.Serializer):
    class Meta:
        fields = ('name', 'id', 'size', 'pg_num', 'crush_ruleset', 'min_size', 'crash_replay_interval', 'crush_ruleset',
                  'pgp_num', 'hashpspool', 'full', 'quota_max_objects', 'quota_max_bytes')

    # Required in creation
    name = serializers.CharField(source='pool_name')
    pg_num = serializers.IntegerField()

    # Not required in creation, immutable
    id = serializers.CharField(source='pool', required=False)

    # May be set in creation or updates
    size = serializers.IntegerField(required=False)
    min_size = serializers.IntegerField(required=False)
    crash_replay_interval = serializers.IntegerField(required=False)
    crush_ruleset = serializers.IntegerField(required=False)
    # In 'ceph osd pool set' it's called pgp_num, but in 'ceph osd dump' it's called
    # pg_placement_num :-/
    pgp_num = serializers.IntegerField(source='pg_placement_num', required=False)

    # This is settable by 'ceph osd pool set' but in 'ceph osd dump' it only appears
    # within the 'flags' integer.  We synthesize a boolean from the flags.
    hashpspool = serializers.BooleanField(required=False)

    # This is synthesized from ceph's 'flags' attribute, read only.
    full = serializers.BooleanField(required=False)

    quota_max_objects = serializers.IntegerField(required=False)
    quota_max_bytes = serializers.IntegerField(required=False)


class CrushRuleSerializer(serializers.Serializer):
    class Meta:
        fields = ('id', 'name', 'ruleset', 'type', 'min_size', 'max_size', 'steps')

    id = serializers.IntegerField(source='rule_id')
    name = serializers.CharField(source='rule_name')
    ruleset = serializers.IntegerField()
    type = serializers.IntegerField()
    min_size = serializers.IntegerField()
    max_size = serializers.IntegerField()
    steps = serializers.Field()


class CrushRuleSetSerializer(serializers.Serializer):
    class Meta:
        fields = ('id', 'rules',)

    id = serializers.IntegerField()
    rules = CrushRuleSerializer(many=True)


class RequestSerializer(serializers.Serializer):
    class Meta:
        fields = ('id', 'state')

    id = serializers.CharField()
    state = serializers.CharField()
