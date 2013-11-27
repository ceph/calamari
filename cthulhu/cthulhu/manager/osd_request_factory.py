from cthulhu.manager.request_factory import RequestFactory
from cthulhu.manager.user_request import OsdMapModifyingRequest


class OsdRequestFactory(RequestFactory):
    def update(self, osd_id, attributes):
        commands = []
        if attributes['in'] == 0:
            commands.append(('osd out', {'ids': [attributes['id'].__str__()]}))
        else:
            commands.append(('osd out', {'ids': [attributes['id'].__str__()]}))

        # TODO: provide some per-object-type ability to emit human readable descriptions
        # of what we are doing.

        # TOOD: provide some machine-readable indication of which objects are affected
        # by a particular request.
        # Perhaps subclass Request for each type of object, and have that subclass provide
        # both the patches->commands mapping and the human readable and machine readable
        # descriptions of it?
        return OsdMapModifyingRequest(self._cluster_monitor.fsid, self._cluster_monitor.name, commands)
