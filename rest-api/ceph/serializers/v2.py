

from rest_framework import serializers


class ClusterSerializer(serializers.Serializer):
    class Meta:
        fields = ('update_time', 'id', 'name')

    update_time = serializers.DateTimeField()
    name = serializers.Field()
    id = serializers.Field()


class SyncObjectSerializer(serializers.Serializer):
    class Meta:
        fields = ('data',)

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
        fields = ('id', 'state', 'error')

    id = serializers.CharField()
    state = serializers.CharField()
    error = serializers.BooleanField()


class SaltKeySerializer(serializers.Serializer):
    class Meta:
        fields = ('id', 'status')

    id = serializers.CharField()
    status = serializers.CharField()


class ServiceSerializer(serializers.Serializer):
    class Meta:
        fields = ('fsid', 'type', 'id', 'running')

    fsid = serializers.SerializerMethodField("get_fsid")
    type = serializers.SerializerMethodField("get_type")
    id = serializers.SerializerMethodField("get_id")
    running = serializers.BooleanField()

    def get_fsid(self, obj):
        return obj['id'][0]

    def get_type(self, obj):
        return obj['id'][1]

    def get_id(self, obj):
        return obj['id'][2]


class SimpleServerSerializer(serializers.Serializer):
    class Meta:
        fields = ('fqdn', 'hostname', 'managed', 'last_contact', 'services')

    # Identifying information
    fqdn = serializers.CharField()
    hostname = serializers.CharField()

    # Calamari monitoring status
    managed = serializers.BooleanField()
    last_contact = serializers.DateTimeField()

    # Ceph usage
    services = ServiceSerializer(many=True)


class ServerSerializer(SimpleServerSerializer):
    class Meta:
        fields = ('fqdn', 'hostname', 'services', 'frontend_addr', 'backend_addr',
                  'frontend_iface', 'backend_iface', 'managed', 'last_contact')

    # Ceph network configuration
    frontend_addr = serializers.CharField()  # may be null if no OSDs or mons on server
    backend_addr = serializers.CharField()  # may be null if no OSDs on server
    frontend_iface = serializers.CharField()  # may be null if interface for frontend addr not up
    backend_iface = serializers.CharField()  # may be null if interface for backend addr not up
