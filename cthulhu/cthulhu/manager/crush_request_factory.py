from cthulhu.manager.request_factory import RequestFactory
from cthulhu.manager.user_request import OsdMapModifyingRequest


class CrushRequestFactory(RequestFactory):
    def update(self, osd_id, attributes):
        commands = [('osd setcrushmap', {'data': attributes})]
        message = "Replacing CRUSH map in {cluster_name}".format(cluster_name=self._cluster_monitor.name)
        return OsdMapModifyingRequest(message, self._cluster_monitor.fsid, self._cluster_monitor.name, commands)
