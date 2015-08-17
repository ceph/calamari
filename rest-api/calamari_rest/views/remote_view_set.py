import logging
from dateutil.parser import parse as dateutil_parse
import salt.client

from calamari_common.config import CalamariConfig
from calamari_common.types import ServiceId, MON
from calamari_rest.views.exceptions import ServiceUnavailable
from calamari_rest.views.rpc_view import RPCViewSet

log = logging.getLogger('django.request')
config = CalamariConfig()


class RemoteViewSet(RPCViewSet):
    """
A ViewSet for API resources which will run remote operations directly on the Ceph cluster,
out of band with respect to cthulhu.  Useful for special cases, but don't use this for
adding new management functionality.
    """
    def _get_up_mon_servers(self, fsid):
        # Resolve FSID to list of mon FQDNs
        servers = self.client.server_list_cluster(fsid)
        # Sort to get most recently contacted server first; drop any
        # for whom last_contact is None
        servers = [s for s in servers if s['last_contact']]
        servers = sorted(servers,
                         key=lambda t: dateutil_parse(t['last_contact']),
                         reverse=True)
        mon_fqdns = []
        for server in servers:
            for service in server['services']:
                service_id = ServiceId(*(service['id']))
                if service['running'] and service_id.service_type == MON and service_id.fsid == fsid:
                    mon_fqdns.append(server['fqdn'])

        return mon_fqdns

    def run_mon_job(self, fsid, job_cmd, job_args):
        """
        Attempt to run a Salt job on a mon server, trying each until we find one
        where the job runs (where running includes running and returning an error)
        """

        # TODO: in order to support radosgw-admin commands we might need to be able to identify running RGW services
        # alternatively it may be possible to run radosgw-admin on a mon node that isn't running the RGW service
        mon_fqdns = self._get_up_mon_servers(fsid)

        client = salt.client.LocalClient(config.get('cthulhu', 'salt_config_path'))
        log.debug("RemoteViewSet: mons for %s are %s" % (fsid, mon_fqdns))
        # For each mon FQDN, try to go get ceph/$cluster.log, if we succeed return it, if we fail try the next one
        # NB this path is actually customizable in ceph as `mon_cluster_log_file` but we assume user hasn't done that.
        for mon_fqdn in mon_fqdns:
            results = client.cmd(mon_fqdn, job_cmd, job_args)
            if results:
                return results[mon_fqdn]
            else:
                log.info("Failed execute mon command on %s" % mon_fqdn)

        # If none of the mons gave us what we wanted, return a 503 service unavailable
        raise ServiceUnavailable("No mon servers are responding")

    def run_job(self, fqdn, job_cmd, job_args):
        """
        Attempt to run a Salt job on a specific server.
        """
        client = salt.client.LocalClient(config.get('cthulhu', 'salt_config_path'))
        results = client.cmd(fqdn, job_cmd, job_args)
        if not results:
            raise ServiceUnavailable("Server '{0}' not responding".format(fqdn))
        else:
            return results[fqdn]
