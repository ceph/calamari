from cthulhu.log import log
from cthulhu.manager.request_factory import RequestFactory
from calamari_common.types import OsdMap, Config
from cthulhu.manager.user_request import OsdMapModifyingRequest, PgCreatingRequest, PoolCreatingRequest

# Valid values for the 'var' argument to 'ceph osd pool set'
POOL_PROPERTIES = ["size", "min_size", "crash_replay_interval", "pg_num", "pgp_num", "crush_ruleset", "hashpspool"]

# In Ceph versions before mon_osd_max_split_count, assume it is set to this
LEGACY_MON_OSD_MAX_SPLIT_COUNT = "32"


class PoolRequestFactory(RequestFactory):
    def _resolve_pool(self, pool_id):
        osd_map = self._cluster_monitor.get_sync_object(OsdMap)
        return osd_map.pools_by_id[pool_id]

    def _pool_attribute_commands(self, pool_name, attributes):
        commands = []
        for var in POOL_PROPERTIES:
            if var in attributes:
                val = attributes[var]

                # Special case for hashpspool, accepts 'true' from firefly onwards
                # but requires 0 or 1 for dumpling, so just use the old style.
                if isinstance(val, bool):
                    val = 1 if val else 0

                commands.append(('osd pool set', {
                    'pool': pool_name,
                    'var': var,
                    'val': val
                }))

        # Quota setting ('osd pool set-quota') is separate to the main 'set' operation
        for attr_name, set_name in [('quota_max_bytes', 'max_bytes'), ('quota_max_objects', 'max_objects')]:
            if attr_name in attributes:
                commands.append(('osd pool set-quota', {
                    'pool': pool_name,
                    'field': set_name,
                    'val': attributes[attr_name].__str__()  # set-quota wants a string in case it has units in
                }))

        # Renames come last (the preceding commands reference the pool by its old name)
        if 'name' in attributes:
            commands.append(('osd pool rename', {
                "srcpool": pool_name,
                "destpool": attributes['name']
            }))

        return commands

    def delete(self, pool_id):
        # Resolve pool ID to name
        pool_name = self._resolve_pool(pool_id)['pool_name']

        # TODO: perhaps the REST API should have something in the body to
        # make it slightly harder to accidentally delete a pool, to respect
        # the severity of this operation since we're hiding the --yes-i-really-really-want-to
        # stuff here
        # TODO: handle errors in a way that caller can show to a user, e.g.
        # if the name is wrong we should be sending a structured errors dict
        # that they can use to associate the complaint with the 'name' field.
        commands = [
            ('osd pool delete', {'pool': pool_name, 'pool2': pool_name, 'sure': '--yes-i-really-really-mean-it'})]
        return OsdMapModifyingRequest("Deleting pool '{name}'".format(name=pool_name),
                                      self._cluster_monitor.fsid, self._cluster_monitor.name, commands)

    def _pool_min_size(self, req_size, req_min_size):
        '''
        Find an appropriate "min_size" parameter for a pool create operation
        req_size is requested pool size; 0 means "use osd_pool_default_size"
        req_min_size is requested min size

        Used in both create and update
        '''
        ceph_config = self._cluster_monitor.get_sync_object_data(Config)
        size = req_size or int(ceph_config.get('osd_pool_default_size'), 0)
        min_size = req_min_size or \
            int(ceph_config.get('osd_pool_default_min_size'), 0)
        if min_size:
            ret_min_size = min(min_size, size)
        else:
            ret_min_size = size - size / 2
        log.info('_pool_min_size: size %d, min_size %d, ret %d' %
                 (size, min_size, ret_min_size))
        return ret_min_size

    def update(self, pool_id, attributes):
        osd_map = self._cluster_monitor.get_sync_object(OsdMap)
        pool = self._resolve_pool(pool_id)
        pool_name = pool['pool_name']

        # Recalculate/clamp min_size if it or size is updated
        if 'size' in attributes or 'min_size' in attributes:
            size = attributes.get('size', pool['size'])
            min_size = attributes.get('min_size', pool['min_size'])
            attributes['min_size'] = self._pool_min_size(size, min_size)

        if 'pg_num' in attributes:
            # Special case when setting pg_num: have to do some extra work
            # to wait for PG creation between setting these two fields.
            final_pg_count = attributes['pg_num']

            if 'pgp_num' in attributes:
                pgp_num = attributes['pgp_num']
                del attributes['pgp_num']
            else:
                pgp_num = attributes['pg_num']
            del attributes['pg_num']

            pre_create_commands = self._pool_attribute_commands(pool_name, attributes)

            # This setting is new in Ceph Firefly, where it defaults to 32.  For older revisions, we simply
            # pretend that the setting exists with a default setting.
            mon_osd_max_split_count = int(self._cluster_monitor.get_sync_object_data(Config).get(
                'mon_osd_max_split_count', LEGACY_MON_OSD_MAX_SPLIT_COUNT))
            initial_pg_count = pool['pg_num']
            n_osds = min(initial_pg_count, len(osd_map.osds_by_id))
            # The rules about creating PGs:
            #  where N_osds = min(old_pg_count, osd_count)
            #    the number of new PGs divided by N_osds may not be greater than mon_osd_max_split_count
            block_size = mon_osd_max_split_count * n_osds

            return PgCreatingRequest(
                "Growing pool '{name}' to {size} PGs".format(name=pool_name, size=final_pg_count),
                self._cluster_monitor.fsid, self._cluster_monitor.name,
                pre_create_commands,
                pool_id, pool_name, pgp_num,
                initial_pg_count, final_pg_count, block_size)
        else:
            commands = self._pool_attribute_commands(pool_name, attributes)
            if not commands:
                raise NotImplementedError(attributes)

            # TODO: provide some machine-readable indication of which objects are affected
            # by a particular request.
            # Perhaps subclass Request for each type of object, and have that subclass provide
            # both the patches->commands mapping and the human readable and machine readable
            # descriptions of it?

            # Objects may be decorated with 'id' from use in a bulk PATCH, but we don't want anything
            # from this point onwards to see that.
            if 'id' in attributes:
                del attributes['id']
            return OsdMapModifyingRequest(
                "Modifying pool '{name}' ({attrs})".format(
                    name=pool_name, attrs=", ".join("%s=%s" % (k, v) for k, v in attributes.items())
                ), self._cluster_monitor.fsid, self._cluster_monitor.name, commands)

    def create(self, attributes):
        commands = [('osd pool create', {'pool': attributes['name'],
                                         'pg_num': attributes['pg_num'],
                                         'pool_type': attributes['type'],
                                         'erasure_code_profile': attributes['erasure_code_profile']})]

        # Calculate appropriate min_size, including default if none given
        req_size = attributes.get('size', 0)
        req_min_size = attributes.get('min_size', 0)
        attributes['min_size'] = self._pool_min_size(req_size, req_min_size)

        # Which attributes must we set after the initial create?
        post_create_attrs = attributes.copy()
        del post_create_attrs['name']
        del post_create_attrs['pg_num']
        if 'pgp_num' in post_create_attrs:
            del post_create_attrs['pgp_num']

        commands.extend(self._pool_attribute_commands(
            attributes['name'],
            post_create_attrs
        ))

        log.debug("Post-create attributes: %s" % post_create_attrs)
        log.debug("Commands: %s" % commands)

        return PoolCreatingRequest(
            "Creating pool '{name}'".format(name=attributes['name']),
            self._cluster_monitor.fsid, self._cluster_monitor.name,
            attributes['name'], commands)
