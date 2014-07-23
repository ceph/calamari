from cthulhu.manager.request_factory import RequestFactory
from cthulhu.manager.user_request import OsdMapModifyingRequest


class CrushRequestFactory(RequestFactory):
    def update(self, osd_id, attributes):
        commands = []

        # send text and handle it in ceph.py
        #   3. What format is the output of CrushTool on error
        # `osd_map = self._cluster_monitor.get_sync_object(OsdMap)

        # TODO hard-code an example crush map here. See is get set
        # commands.append(('osd in', {'ids': [attributes['id'].__str__()]}))
        commands.append(('osd getcrushmap', {}))

        # raise RuntimeError("It is not valid to set a down OSD to be up")

        if not commands:
            # Returning None indicates no-op
            return None

        msg_attrs = attributes.copy()
        del msg_attrs['id']

        if msg_attrs.keys() == ['in']:
            message = "Replacing CRUSH map in {cluster_name}".format(
                cluster_name=self._cluster_monitor.name)

        return OsdMapModifyingRequest(message, self._cluster_monitor.fsid, self._cluster_monitor.name, commands)
