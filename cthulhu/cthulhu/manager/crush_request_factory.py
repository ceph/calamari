import logging

from cthulhu.manager.request_factory import RequestFactory
from cthulhu.manager.user_request import OsdMapModifyingRequest


log = logging.getLogger('crush_request_factory')

class CrushRequestFactory(RequestFactory):
    def update(self, osd_id, attributes):
        commands = []

        # commands.append(('osd in', {'ids': [attributes['id'].__str__()]}))
        commands.append(('osd setcrushmap', {'data': attributes}))

        log.error(str(attributes))
        # raise RuntimeError("It is not valid to set a down OSD to be up")

        if not commands:
            # Returning None indicates no-op
            return None

        message = "Replacing CRUSH map in {cluster_name}".format(cluster_name=self._cluster_monitor.name)

        return OsdMapModifyingRequest(message, self._cluster_monitor.fsid, self._cluster_monitor.name, commands)
