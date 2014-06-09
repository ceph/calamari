
import logging
import re
import gevent

from calamari_common.remote.base import Remote, Unavailable, AUTH_REJECTED, AUTH_NEW, AUTH_ACCEPTED
from calamari_common.salt_wrapper import master_config, _create_loader, client_config, MasterPillarUtil, LocalClient, condition_kwarg, \
    SaltEventSource, Key
from calamari_common.config import CalamariConfig
from calamari_common.types import SERVER, NotFound


log = logging.getLogger('calamari.remote.salt')
config = CalamariConfig()
salt_config = client_config(config.get('cthulhu', 'salt_config_path'))


# Issue up to this many disk I/Os to load grains at once
CONCURRENT_GRAIN_LOADS = 16


class SaltRemote(Remote):
    def run_job_sync(self, fqdn, cmd, args, timeout=None):
        client = LocalClient(config.get('cthulhu', 'salt_config_path'))
        results = client.cmd(fqdn, cmd, args, timeout=timeout)
        if results:
            if isinstance(fqdn, list):
                return results
            else:
                return results[fqdn]
        else:
            raise Unavailable()

    def run_job(self, fqdn, cmd, args):
        client = LocalClient(config.get('cthulhu', 'salt_config_path'))
        pub_data = client.run_job(fqdn, cmd, condition_kwarg([], args))
        if not pub_data:
            # FIXME: LocalClient uses 'print' to record the
            # details of what went wrong :-(
            raise Unavailable()
        else:
            return pub_data['jid']

    def get_local_metadata(self):
        # Stash grains as an attribute of this function
        if not hasattr(SaltRemote, 'grains'):
            # >> work around salt issue #11402
            import __main__ as main
            main.__file__ = 'workaround'
            # <<

            # Use salt to get an interesting subset of the salt grains (getting
            # everything is a bit slow)
            grains = {}
            c = master_config(config.get('cthulhu', 'salt_config_path'))
            l = _create_loader(c, 'grains', 'grain')
            funcs = l.gen_functions()
            for key in [k for k in funcs.keys() if k.startswith('core.')]:
                ret = funcs[key]()
                if isinstance(ret, dict):
                    grains.update(ret)
            SaltRemote.grains = grains
        else:
            grains = SaltRemote.grains

        return grains

    def get_remote_metadata(self, fqdns):
        pillar_util = MasterPillarUtil('', 'glob',
                                       use_cached_grains=True,
                                       grains_fallback=False,
                                       opts=salt_config)

        fqdn_to_grains = {}

        def _lookup_one(fqdn):
            log.debug(">> resolving grains for server {0}".format(fqdn))
            cache_grains, cache_pillar = pillar_util._get_cached_minion_data(fqdn)

            if fqdn not in cache_grains:
                fqdn_to_grains[fqdn] = {}
            else:
                fqdn_to_grains[fqdn] = cache_grains[fqdn]

            log.debug("<< resolving grains for server {0}".format(fqdn))

        p = gevent.pool.Pool(CONCURRENT_GRAIN_LOADS)
        p.map(_lookup_one, fqdns)

        return fqdn_to_grains

    def get_heartbeat_period(self, fqdn):
        pillar_util = MasterPillarUtil([fqdn], 'list',
                                       grains_fallback=False,
                                       pillar_fallback=False,
                                       opts=salt_config)

        try:
            return pillar_util.get_minion_pillar()[fqdn]['schedule']['ceph.heartbeat']['seconds']
        except KeyError:
            # Just in case salt pillar is unavailable for some reason, a somewhat sensible
            # guess.  It's really an error, but I don't want to break the world in this case.
            fallback_contact_period = 60
            log.warn("Missing period in minion '{0}' pillar".format(fqdn))
            return fallback_contact_period

    def get_running(self, minions):
        client = LocalClient(config.get('cthulhu', 'salt_config_path'))
        pub_data = client.run_job(minions, 'saltutil.running', [], expr_form="list")
        if not pub_data:
            log.warning("Failed to publish saltutil.running to {0}".format(minions))

    def cancel(self, fqdn, jid):
        client = LocalClient(config.get('cthulhu', 'salt_config_path'))
        client.run_job(fqdn, 'saltutil.kill_job', [jid])

    @property
    def _salt_key(self):
        return Key(master_config(config.get('cthulhu', 'salt_config_path')))

    def auth_get(self, minion_id):
        # FIXME: I think we're supposed to use salt.wheel.Wheel.master_call
        # for this stuff to call out to the master instead of touching
        # the files directly (need to set up some auth to do that though)

        result = self._salt_key.name_match(minion_id, full=True)
        if not result:
            raise NotFound(SERVER, minion_id)

        if 'minions' in result:
            status = AUTH_ACCEPTED
        elif "minions_pre" in result:
            status = AUTH_NEW
        elif "minions_rejected" in result:
            status = AUTH_REJECTED
        else:
            raise ValueError(result)

        return {
            'id': minion_id,
            'status': status
        }

    def auth_list(self, status_filter):
        keys = self._salt_key.list_keys()
        result = []

        key_to_status = {
            'minions_pre': 'pre',
            'minions_rejected': 'rejected',
            'minions': 'accepted'
        }

        for key, status in key_to_status.items():
            for minion in keys[key]:
                if not status_filter or status == status_filter:
                    result.append({
                        'id': minion,
                        'status': status
                    })

        return result

    def auth_accept(self, fqdn):
        return self._salt_key.accept(fqdn)

    def auth_reject(self, fqdn):
        return self._salt_key.reject(fqdn)

    def auth_delete(self, fqdn):
        return self._salt_key.delete_key(fqdn)

    def listen(self, completion,
               on_heartbeat=None,
               on_job=None,
               on_server_heartbeat=None,
               on_running_jobs=None,
               fsid=None):
        """
        :param on_heartbeat: Callback for heartbeats
        :param on_job: Callback for job completions
        :param fsid: Optionally filter heartbeats to one FSID
        """

        event = SaltEventSource(log, salt_config)

        if fsid:
            heartbeat_tag = "ceph/cluster/{0}".format(fsid)
        else:
            heartbeat_tag = "ceph/cluster/"

        while not completion.is_set():
            # No salt tag filtering: https://github.com/saltstack/salt/issues/11582
            ev = event.get_event(full=True)

            if ev is not None:
                data = ev['data']
                tag = ev['tag']
                log.debug("_run.ev: %s/tag=%s" % (data['id'] if 'id' in data else None, tag))

                # I am interested in the following tags:
                # - salt/job/<jid>/ret/<minion id> where jid is one that I started
                #   (this includes ceph.rados_command and ceph.get_cluster_object)
                # - ceph/cluster/<fsid> where fsid is my fsid

                try:
                    if tag.startswith(heartbeat_tag):
                        if on_heartbeat:
                            on_heartbeat(data['id'], data['data'])
                    elif tag.startswith("ceph/server"):
                        if on_server_heartbeat:
                            on_server_heartbeat(data['id'], data['data'])
                    elif re.match("^salt/job/\d+/ret/[^/]+$", tag):
                        if data['fun'] == 'saltutil.running':
                            if on_running_jobs and data['success']:
                                on_running_jobs(data['id'], data['return'])
                        else:
                            if on_job:
                                on_job(data['id'], data['jid'], data['success'], data['return'],
                                       data['fun'], data['fun_args'])
                    else:
                        # This does not concern us, ignore it
                        pass
                except:
                    # Because this is our main event handling loop, swallow exceptions
                    # instead of letting them end the world.
                    log.exception("Exception handling message with tag %s" % tag)
                    log.debug("Message content: %s" % data)
