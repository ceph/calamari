from cthulhu.manager.request_factory import RequestFactory
from cthulhu.manager.user_request import OsdMapModifyingRequest
from cthulhu.log import log
from calamari_common.types import OsdMap


class CachePoolRequestFactory(RequestFactory):

    def create(self, attributes):
        commands = [('osd tier add', {"pool": attributes['pool'], "tierpool": attributes['tier_pool']})]
        if 'mode' in attributes and attributes['mode'] is not None:
            commands.append(('osd tier cache-mode', {'pool': attributes['tier_pool'], 'mode': attributes['mode']}))
            if attributes['mode'] == 'write_back':
                commands.append(
                    ('osd tier set-overlay', {"pool": attributes['pool'], "overlaypool": attributes['tier_pool']}))
        else:
            log.warn("there is not cache-mode")
        message = "Creating cache pool {cache_pool_name} for pool {pool_name}".format(
            pool_name=attributes['pool'], cache_pool_name=attributes['tier_pool'])
        return OsdMapModifyingRequest(message, self._cluster_monitor.fsid, self._cluster_monitor.name, commands)

    def delete(self, attributes):
        pool_id = attributes['pool']
        tier_pool_id = attributes['tier_pool']
        tier_name = self._resolve_pool(tier_pool_id)['pool_name']
        pool_name = self._resolve_pool(pool_id)['pool_name']
        cache_mode = self._resolve_pool(pool_id)['cache_mode']
        commands = []
        if cache_mode == "write_back":
            commands.append(('osd tier remove-overlay', {'pool': pool_name}))
        commands.append(('osd tier remove', {"pool": pool_name, "tierpool": tier_name}))
        message = "Remove cache pool {cache_pool_name} for  pool  {pool_name}".format(
            pool_name=pool_name, cache_pool_name=tier_name)
        return OsdMapModifyingRequest(message, self._cluster_monitor.fsid, self._cluster_monitor.name, commands)

    def _resolve_pool(self, pool_id):
        osd_map = self._cluster_monitor.get_sync_object(OsdMap)
        if pool_id not in osd_map.pools_by_id:
            log.error("there is not pool id %s in osd_map" % pool_id)
            raise "there is not pool id %s in osd_map" % pool_id
        return osd_map.pools_by_id[pool_id]

    def update(self, object_id, attributes):
        commands = []
        self._set_cache_mode(attributes, commands)
        message = "Update cache pool id  {pool_name} for cache_pool mode {cache_mode}".format(
            pool_name=object_id, cache_mode=attributes['mode'])
        return OsdMapModifyingRequest(message, self._cluster_monitor.fsid, self._cluster_monitor.name, commands)

    def _set_cache_mode(self, attributes, commands=[]):
        if 'mode' in attributes and attributes['mode'] is not None:
            commands.append(('osd tier cache-mode', {'pool':  attributes['tierpool'], 'mode': attributes['mode']}))
            if attributes['mode'] == 'write_back':
                commands.append(('osd tier set-overlay', {
                    "pool": attributes['pool'], "overlaypool": attributes['tier_pool']}))
        else:
            log.warn("there is not cache-mode")
