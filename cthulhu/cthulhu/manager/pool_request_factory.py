from cthulhu.log import log
from cthulhu.manager.request_factory import RequestFactory
from cthulhu.manager.types import OsdMap
from cthulhu.manager.user_request import OsdMapModifyingRequest, PgCreatingRequest

# Valid values for the 'var' argument to 'ceph osd pool set'
POOL_PROPERTIES = ["size", "min_size", "crash_replay_interval", "pg_num", "pgp_num", "crush_ruleset", "hashpspool"]


class PoolRequestFactory(RequestFactory):
    def _resolve_pool(self, pool_id):
        for pool in self._cluster_monitor.get_sync_object_data(OsdMap)['pools']:
            if pool['pool'] == pool_id:
                return pool
        else:
            raise ValueError("Pool %s not found" % pool_id)

    def _pool_attribute_commands(self, pool_name, attributes):
        commands = []
        for var in POOL_PROPERTIES:
            if var in attributes:
                val = attributes[var]
                if isinstance(val, bool):
                    val = "true" if val else "false"

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

        # Renames come last (the preceeding commands reference the pool by its old name)
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

    def update(self, pool_id, attributes):
        # TODO: this is a primitive form of adding PGs, not yet sufficient for
        # real use because it leaves pgp_num unset.
        pool_name = self._resolve_pool(pool_id)['pool_name']

        if 'pg_num' in attributes and 'pgp_num' in attributes:
            # Special case when setting pgp_num and pg_num: have to do some extra work
            # to wait for PG creation between setting these two fields.
            pgp_num = attributes['pgp_num']
            del attributes['pgp_num']
            pre_create_commands = self._pool_attribute_commands(pool_name, attributes)
            post_create_commands = [("osd pool set", {'pool': pool_name, 'var': 'pgp_num', 'val': pgp_num})]
            expected_pgs = attributes['pg_num']
            return PgCreatingRequest(
                "Growing pool '{name}' to {size} PGs".format(name=pool_name, size=expected_pgs),
                self._cluster_monitor.fsid, self._cluster_monitor.name,
                pre_create_commands, post_create_commands, pool_id, expected_pgs)
        else:
            commands = self._pool_attribute_commands(pool_name, attributes)
            if not commands:
                raise NotImplementedError(attributes)

            # TOOD: provide some machine-readable indication of which objects are affected
            # by a particular request.
            # Perhaps subclass Request for each type of object, and have that subclass provide
            # both the patches->commands mapping and the human readable and machine readable
            # descriptions of it?
            return OsdMapModifyingRequest(
                "Modifying pool '{name}' ({attrs})".format(
                    name=pool_name, attrs=", ".join("%s=%s" % (k, v) for k, v in attributes.items())
                ), self._cluster_monitor.fsid, self._cluster_monitor.name, commands)

    def create(self, attributes):
        # TODO: handle errors in a way that caller can show to a user, e.g.
        # if the name is wrong we should be sending a structured errors dict
        # that they can use to associate the complaint with the 'name' field.
        commands = [('osd pool create', {'pool': attributes['name'], 'pg_num': attributes['pg_num']})]

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
        log.debug("Commands: %s" % post_create_attrs)

        return OsdMapModifyingRequest(
            "Creating pool '{name}'".format(name=attributes['name']),
            self._cluster_monitor.fsid, self._cluster_monitor.name, commands)
