from cthulhu.manager.request_factory import RequestFactory
from cthulhu.manager.types import OsdMap, OSD_IMPLEMENTED_COMMANDS
from cthulhu.manager.user_request import OsdMapModifyingRequest, UserRequest


class OsdRequestFactory(RequestFactory):

    def update(self, osd_id, attributes):
        commands = []

        osd_map = self._cluster_monitor.get_sync_object(OsdMap)

        # in/out/down take a vector of strings called 'ids', while 'reweight' takes a single integer

        if 'in' in attributes and bool(attributes['in']) != bool(osd_map.osds_by_id[osd_id]['in']):
            if attributes['in']:
                commands.append(('osd in', {'ids': [attributes['id'].__str__()]}))
            else:
                commands.append(('osd out', {'ids': [attributes['id'].__str__()]}))

        if 'up' in attributes and bool(attributes['up']) != bool(osd_map.osds_by_id[osd_id]['up']):
            if not attributes['up']:
                commands.append(('osd down', {'ids': [attributes['id'].__str__()]}))
            else:
                raise RuntimeError("It is not valid to set a down OSD to be up")

        if 'reweight' in attributes:
            if attributes['reweight'] != osd_map.osd_tree_node_by_id[osd_id]['reweight']:
                commands.append(('osd reweight', {'id': osd_id, 'weight': attributes['reweight']}))

        if not commands:
            # Returning None indicates no-op
            return None

        print_attrs = attributes.copy()
        del print_attrs['id']

        return OsdMapModifyingRequest(
            "Modifying {cluster_name}-osd.{id} ({attrs})".format(
                cluster_name=self._cluster_monitor.name, id=osd_id, attrs=", ".join("%s=%s" % (k, v) for k, v in print_attrs.items())
            ), self._cluster_monitor.fsid, self._cluster_monitor.name, commands)

    def scrub(self, osd_id):
        return UserRequest("Scrubbing {cluster_name}-osd.{id}".format(cluster_name=self._cluster_monitor.fsid, id=osd_id),
                           self._cluster_monitor.fsid,
                           self._cluster_monitor.name,
                           [('osd scrub', {'who': str(osd_id)})])

    def deep_scrub(self, osd_id):
        return UserRequest("Deep-scrubbing {cluster_name}-osd.{id}".format(cluster_name=self._cluster_monitor.fsid, id=osd_id),
                           self._cluster_monitor.fsid,
                           self._cluster_monitor.name,
                           [('osd deep-scrub', {'who': str(osd_id)})])


    def repair(self, osd_id):
        return UserRequest("Repairing {cluster_name}-osd.{id}".format(cluster_name=self._cluster_monitor.fsid, id=osd_id),
                           self._cluster_monitor.fsid,
                           self._cluster_monitor.name,
                           [('osd repair', {'who': str(osd_id)})])


    def get_valid_commands(self, osds):
        """
        For each OSD in osds list valid commands
        """
        ret_val = {}
        osd_map = self._cluster_monitor.get_sync_object(OsdMap)
        for osd_id in osds:
            try:
                if osd_map.osds_by_id[osd_id]['up']:
                    ret_val[osd_id] = {'valid_commands': OSD_IMPLEMENTED_COMMANDS}
                else:
                    ret_val[osd_id] = {'valid_commands': []}
            except KeyError:
                pass

        return ret_val
