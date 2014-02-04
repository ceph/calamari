from rest_framework import serializers


class BooleanField(serializers.BooleanField):
    """
    Version of BooleanField which handles fields which are 1,0
    """
    def to_native(self, value):
        if isinstance(value, int) and value in [0, 1]:
            return bool(value)
        else:
            super(BooleanField, self).to_native(value)


class UuidField(serializers.CharField):
    """
    For strings like Ceph service UUIDs and Ceph cluster FSIDs
    """
    type_name = "UuidField"
    type_label = "uuid string"
