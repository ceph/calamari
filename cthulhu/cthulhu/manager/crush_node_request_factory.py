from cthulhu.manager.request_factory import RequestFactory
from cthulhu.manager.user_request import OsdMapModifyingRequest
from cthulhu.manager.server_monitor import ServiceId
from calamari_common.types import OSD, OsdMap, BucketNotEmptyError
import json

import logging

log = logging.getLogger('cthulhu.crush_node_request_factory')


class CrushNodeRequestFactory(RequestFactory):
    """
    Map REST API verbs onto CLI reality
    """
    def __init__(self, monitor):
        super(CrushNodeRequestFactory, self).__init__(monitor)
        self.osd_map = self._cluster_monitor.get_sync_object(OsdMap)
        # HERE we have access to the cluster_monitor and likely the server monitor
        self._server_monitor = monitor._servers
        self.fsid = self._cluster_monitor.fsid

    def update(self, node_id, attributes):
        # TODO report Not Modified http://tracker.ceph.com/issues/9764
        current_node = self.osd_map.get_tree_node(node_id)
        parent = self.osd_map.parent_bucket_by_node_id.get(node_id, None)
        name, bucket_type, items = [attributes[key] for key in ('name', 'bucket_type', 'items')]
        commands = []

        # TODO change to use rename-bucket when #9526 lands in ceph 0.89
        if name != current_node['name'] or bucket_type != current_node['type_name']:
            commands.append(add_bucket(name, bucket_type))
            if parent is not None:
                commands.append(move_bucket(name, parent['name'], parent['type']))

        to_remove = [item for item in current_node['items'] if item not in items]
        commands += self._remove_items(name, bucket_type, to_remove)
        for c in self._add_items(name, bucket_type, items):
                if c not in commands:
                        commands.append(c)

        if name != current_node['name'] or bucket_type != current_node['type_name']:
            commands.append(remove_bucket(current_node['name'], None))

        log.info("Updating CRUSH node {c} parent {p} version {v}".format(c=commands, p=parent, v=self.osd_map.version))
        message = "Updating CRUSH node in {cluster_name}".format(cluster_name=self._cluster_monitor.name)
        return OsdMapModifyingRequest(message, self._cluster_monitor.fsid, self._cluster_monitor.name, commands)

    def create(self, attributes):
        name, bucket_type, items = [attributes[key] for key in ('name', 'bucket_type', 'items')]
        commands = [add_bucket(name, bucket_type)] +\
            self._add_items(name, bucket_type, items)

        message = "Creating CRUSH node in {cluster_name}".format(cluster_name=self._cluster_monitor.name)
        return OsdMapModifyingRequest(message, self._cluster_monitor.fsid, self._cluster_monitor.name, commands)

    def delete(self, node_id):
        current_node = self.osd_map.get_tree_node(node_id)
        commands = [remove_bucket(current_node['name'], current_node)]
        message = "Removing CRUSH node in {cluster_name}".format(cluster_name=self._cluster_monitor.name)
        return OsdMapModifyingRequest(message, self._cluster_monitor.fsid, self._cluster_monitor.name, commands)

    def _remove_items(self, name, bucket_type, items):
        commands = []
        for item in items:
            id = item['id']
            if id < 0:
                current_node = self.osd_map.get_tree_node(id)
                commands.append(remove_bucket(current_node['name'], current_node))
            else:
                child = 'osd.{id}'.format(id=id)
                commands.append(reweight_osd(child, 0.0))
                commands.append(remove_bucket(child, None))
        return commands

    def _add_items(self, name, bucket_type, items):
        commands = []
        # TODO what about subtrees containing OSDs
        for item in items:
            id = item['id']
            if id < 0:  # bucket case
                child = self.osd_map.get_tree_node(id)['name']
                commands.append(move_bucket(child, name, bucket_type))
            else:  # OSD
                # probe on_osd_map in server_moditor when running
                hostname = self._get_hostname_where_osd_runs(id)

                child = 'osd.{id}'.format(id=id)
                reweight = reweight_osd(child, 0.0)
                if reweight not in commands:
                    commands.append(reweight_osd(child, 0.0))
                remove = remove_bucket(child, None)
                if remove not in commands:
                    commands.append(remove_bucket(child, None))
                commands += move_osd(hostname, id, name, bucket_type)
                commands.append(reweight_osd(child, item['weight']))
        return commands

    def _get_hostname_where_osd_runs(self, osd_id):
        return self._server_monitor.get_by_service(ServiceId(self.fsid,
                                                             OSD,
                                                             str(osd_id))).hostname


def add_bucket(name, bucket_type):
    return ('osd crush add-bucket', {'name': name, 'type': bucket_type},)


def remove_bucket(name, node):
    if node is not None:
        if node['items']:
            raise BucketNotEmptyError('Cannot delete a bucket that still contains items')
    return ('osd crush remove', {'name': name},)


def reweight_osd(name, weight):
    return ('osd crush reweight', {'name': name,
                                   'weight': weight,
                                   },
            )


def move_osd(hostname, osd_id, parent_name, parent_type):

    osd_crush_location = {'parent_type': parent_type,
                          'parent_name': parent_name,
                          'hostname': hostname}

    return (('osd crush add', {'args': ['{type}={name}'.format(type=parent_type,
                                                               name=parent_name)],
                               'id': osd_id,
                               'weight': 0.0,
                               }
             ),
            # TODO do something about not modified, we don't want to store obvious stuff in teh keystore
            # for hostname in the cache what we need to do here is work out what the parent is (host)?
            # and then figure out it's hostname, we know these things in /api/v2/cluster/fsid/server
            # the osd cephx key has limited access to this info already see ceph/src/mon/MonCap.cc:139
            # look for this in the log log.debug("Warning: failed to process CRUSH host->osd mapping")
            ('config-key put', {'key': 'daemon-private/osd.{id}/v1/calamari/osd_crush_location'.format(id=osd_id),
                                'val': json.dumps(osd_crush_location)
                                }
             ))


def move_bucket(name, parent_name, parent_type):
    return ('osd crush move',
            {'name': name,
             'args': ["{type}={name}".format(type=parent_type, name=parent_name)],
             })
