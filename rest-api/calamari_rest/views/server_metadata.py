
"""
Expose metadata for the Calamari server and Ceph servers.

This is a wrapper around the Salt interfaces we use to get this data.
"""
import logging

import gevent.pool

from calamari_common.salt_wrapper import master_config, _create_loader, client_config, MasterPillarUtil
from calamari_common.config import CalamariConfig


log = logging.getLogger('django.request')
config = CalamariConfig()


# Issue up to this many disk I/Os to load grains at once
CONCURRENT_GRAIN_LOADS = 16


def get_grains_from_loader():
    # Use salt to get an interesting subset of the salt grains (getting
    # everything is a bit slow)
    master_conf = master_config(config.get('cthulhu', 'salt_config_path'))
    load = _create_loader(master_conf, 'grains', 'grain')
    # static_loader returns a dict object, _create_loader returns
    # a Loader object. Handle both cases.
    if isinstance(load, dict):
        funcs = load
    else:
        funcs = load.gen_functions()

    return funcs


def get_local_grains():
    """
    Return the salt grains for this host that we are running
    on.  If we support SELinux in the future this may need
    to be moved into a cthulhu RPC as the apache worker may
    not have the right capabilities to query all the grains.
    """
    # Stash grains as an attribute of this function
    if not hasattr(get_local_grains, 'grains'):

        # >> work around salt issue #11402
        import __main__ as main
        main.__file__ = 'workaround'
        # <<

        grains = {}
        funcs = get_grains_from_loader()
        for key in [k for k in funcs.keys() if k.startswith('core.')]:
            ret = funcs[key]()
            if isinstance(ret, dict):
                grains.update(ret)
        get_local_grains.grains = grains
    else:
        grains = get_local_grains.grains

    return grains


def get_remote_grains(fqdns):
    """
    Return a dict of FQDN to grain dictionary for remote servers.

    Any servers for which grains are not found will appear in the result
    with an empty grains dictionary
    """
    salt_config = client_config(config.get('cthulhu', 'salt_config_path'))
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
