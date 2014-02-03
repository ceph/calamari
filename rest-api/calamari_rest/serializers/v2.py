

from rest_framework import serializers
from cthulhu.manager.eventer import severity_str
import calamari_rest.serializers.fields as fields
from cthulhu.manager.user_request import UserRequest


class ClusterSerializer(serializers.Serializer):
    class Meta:
        fields = ('update_time', 'id', 'name')

    update_time = serializers.DateTimeField(
        help_text="The time at which the last status update from this cluster was received"
    )
    name = serializers.Field(
        help_text="Human readable cluster name, not a unique identifier"
    )
    id = serializers.Field(
        help_text="The FSID of the cluster, universally unique"
    )


class PoolSerializer(serializers.Serializer):
    class Meta:
        fields = ('name', 'id', 'size', 'pg_num', 'crush_ruleset', 'min_size', 'crash_replay_interval', 'crush_ruleset',
                  'pgp_num', 'hashpspool', 'full', 'quota_max_objects', 'quota_max_bytes')

    # Required in creation
    name = serializers.CharField(source='pool_name',
                                 help_text="Human readable name of the pool, may"
                                 "change over the pools lifetime at user request.")
    pg_num = serializers.IntegerField(
        help_text="Number of placement groups in this pool")

    # Not required in creation, immutable
    id = serializers.CharField(source='pool', required=False, help_text="Unique numeric ID")

    # May be set in creation or updates
    size = serializers.IntegerField(required=False,
                                    help_text="Replication factor")
    min_size = serializers.IntegerField(required=False,
                                        help_text="Minimum number of replicas required for I/O")
    crash_replay_interval = serializers.IntegerField(required=False,
                                                     help_text="Number of seconds to allow clients to "
                                                               "replay acknowledged, but uncommitted requests")
    crush_ruleset = serializers.IntegerField(required=False, help_text="CRUSH ruleset in use")
    # In 'ceph osd pool set' it's called pgp_num, but in 'ceph osd dump' it's called
    # pg_placement_num :-/
    pgp_num = serializers.IntegerField(source='pg_placement_num', required=False,
                                       help_text="Effective number of placement groups to use when calculating "
                                                 "data placement")

    # This is settable by 'ceph osd pool set' but in 'ceph osd dump' it only appears
    # within the 'flags' integer.  We synthesize a boolean from the flags.
    hashpspool = serializers.BooleanField(required=False, help_text="Enable HASHPSPOOL flag")

    # This is synthesized from ceph's 'flags' attribute, read only.
    full = serializers.BooleanField(required=False, help_text="True if the pool is full")

    quota_max_objects = serializers.IntegerField(required=False,
                                                 help_text="Quota limit on object count (0 is unlimited)")
    quota_max_bytes = serializers.IntegerField(required=False,
                                               help_text="Quota limit on usage in bytes (0 is unlimited)")


class OsdSerializer(serializers.Serializer):
    class Meta:
        fields = ('uuid', 'up', 'in', 'id', 'reweight', 'server', 'pools', 'public_addr', 'cluster_addr')

    id = serializers.IntegerField(source='osd', help_text="ID of this OSD within this cluster")
    uuid = fields.UuidField(help_text="Globally unique ID for this OSD")
    up = fields.BooleanField(help_text="Whether the OSD is running from the point of view of the rest of the cluster")
    _in = fields.BooleanField(help_text="Whether the OSD is 'in' the set of OSDs which will be used to store data")
    reweight = serializers.FloatField(help_text="CRUSH weight factor")
    server = serializers.CharField(help_text="FQDN of server this OSD was last running on")
    pools = serializers.Field(help_text="List of pool IDs which use this OSD for storage")

    public_addr = serializers.CharField(help_text="Public/frontend IP address")
    cluster_addr = serializers.CharField(help_text="Cluster/backend IP address")

# Declarative metaclass definitions are great until you want
# to use a reserved word
OsdSerializer.base_fields['in'] = OsdSerializer.base_fields['_in']


class CrushRuleSerializer(serializers.Serializer):
    class Meta:
        fields = ('id', 'name', 'ruleset', 'type', 'min_size', 'max_size', 'steps', 'osd_count')

    id = serializers.IntegerField(source='rule_id')
    name = serializers.CharField(source='rule_name')
    ruleset = serializers.IntegerField()
    type = serializers.IntegerField()
    min_size = serializers.IntegerField()
    max_size = serializers.IntegerField()
    steps = serializers.Field()
    osd_count = serializers.IntegerField(help_text="Number of OSDs which are used for data placement")


class CrushRuleSetSerializer(serializers.Serializer):
    class Meta:
        fields = ('id', 'rules', 'osd_count')

    id = serializers.IntegerField()
    rules = CrushRuleSerializer(many=True)
    osd_count = serializers.IntegerField(help_text="Number of OSDs which are used for data placement")


class RequestSerializer(serializers.Serializer):
    class Meta:
        fields = ('id', 'state', 'error', 'error_message', 'headline', 'status')

    id = serializers.CharField(help_text="A globally unique ID for this request")
    state = serializers.CharField(help_text="One of '{complete}', '{submitted}'".format(
        complete=UserRequest.COMPLETE, submitted=UserRequest.SUBMITTED))
    error = serializers.BooleanField(help_text="True if the request completed unsuccessfully")
    error_message = serializers.CharField(help_text="Human readable string describing failure if ``error`` is True")
    headline = serializers.CharField(help_text="Single sentence human readable description of the request")
    status = serializers.CharField(help_text="Single sentence human readable description of the request's current "
                                             "activity, if it has more than one stage.  May be null.")


class SaltKeySerializer(serializers.Serializer):
    class Meta:
        fields = ('id', 'status')

    id = serializers.CharField(help_text="The minion ID, usually equal to a host's FQDN")
    status = serializers.CharField(help_text="One of 'accepted', 'rejected' or 'pre'")


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
    fqdn = serializers.CharField(help_text="Fully qualified domain name")
    hostname = serializers.CharField(help_text="Unqualified hostname")

    # Calamari monitoring status
    managed = serializers.BooleanField(
        help_text="True if this server is under Calamari server's control, false"
                  "if the server's existence was inferred via Ceph cluster maps.")
    last_contact = serializers.DateTimeField(
        help_text="The time at which this server last communicated with the Calamari"
                  "server.  This is always null for unmanaged servers")

    # Ceph usage
    services = ServiceSerializer(many=True, help_text="List of Ceph services seen"
                                 "on this server")


class ServerSerializer(SimpleServerSerializer):
    class Meta:
        fields = ('fqdn', 'hostname', 'services', 'frontend_addr', 'backend_addr',
                  'frontend_iface', 'backend_iface', 'managed', 'last_contact')

    # Ceph network configuration
    frontend_addr = serializers.CharField()  # may be null if no OSDs or mons on server
    backend_addr = serializers.CharField()  # may be null if no OSDs on server
    frontend_iface = serializers.CharField()  # may be null if interface for frontend addr not up
    backend_iface = serializers.CharField()  # may be null if interface for backend addr not up


class EventSerializer(serializers.Serializer):
    class Meta:
        fields = ('when', 'severity', 'message')

    when = serializers.DateTimeField(help_text="Time at which event was generated")
    severity = serializers.SerializerMethodField('get_severity')
    # FIXME: django_rest_framework doesn't let me put help_text on a methodfield
    # help_text="Severity, one of %s" % ",".join(SEVERITIES.keys()))
    message = serializers.CharField(help_text="One line human readable description")

    def get_severity(self, obj):
        return severity_str(obj.severity)


class LogTailSerializer(serializers.Serializer):
    """
    Trivial serializer to wrap a string blob of log output
    """
    class Meta:
        fields = ('lines',)

    lines = serializers.CharField("Retrieved log data as a newline-separated string")


class ConfigSettingSerializer(serializers.Serializer):
    class Meta:
        fields = ('key', 'value')

    # This is very simple for now, but later we may add more things like
    # schema information, allowed values, defaults.

    key = serializers.CharField(help_text="Name of the configuration setting")
    value = serializers.CharField(help_text="Current value of the setting, as a string")
