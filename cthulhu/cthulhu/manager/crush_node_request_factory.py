from cthulhu.manager.request_factory import RequestFactory
from cthulhu.manager.user_request import OsdMapModifyingRequest
from calamari_common.types import OsdMap, BucketNotEmptyError
import logging


log = logging.getLogger('cthulhu.crush_node_factory')


class CrushNodeRequestFactory(RequestFactory):
    """
    Map REST API verbs onto CLI reality
    """
    def __init__(self, monitor):
        super(CrushNodeRequestFactory, self).__init__(monitor)
        self.osd_map = self._cluster_monitor.get_sync_object(OsdMap)

    def update(self, node_id, attributes):
        # TODO report No-ops
        current_node = self.osd_map.get_tree_node(node_id)
        parent = self.osd_map.parent_bucket_by_node_id.get(node_id, None)
        name, bucket_type, items = [attributes[key] for key in ('name', 'bucket-type', 'items')]

        to_remove = [item for item in current_node['items'] if item not in items]
        commands = self._remove_items(name, bucket_type, to_remove) + self._add_items(name, bucket_type, items)

        # TODO change to use rename-bucket when #9526 lands in ceph
        if name != current_node['name'] or bucket_type != current_node['type_name']:
            if parent is not None:
                commands = [move_bucket(name, parent['name'], parent['type'])] + commands

            commands = [add_bucket(name, bucket_type)] + commands
            commands.append(remove_bucket(current_node['name'], None))

        log.info("update CRUSH node {c} parent {p} version {v}".format(c=commands, p=self.osd_map.parent_bucket_by_node_id, v=self.osd_map.version))
        message = "update CRUSH bucket in {cluster_name}".format(cluster_name=self._cluster_monitor.name)
        return OsdMapModifyingRequest(message, self._cluster_monitor.fsid, self._cluster_monitor.name, commands)

    def create(self, attributes):
        name, bucket_type, items = [attributes[key] for key in ('name', 'bucket-type', 'items')]
        commands = [add_bucket(name, bucket_type)] +\
            self._add_items(name, bucket_type, items)

        message = "Adding CRUSH bucket in {cluster_name}".format(cluster_name=self._cluster_monitor.name)
        return OsdMapModifyingRequest(message, self._cluster_monitor.fsid, self._cluster_monitor.name, commands)

    def delete(self, node_id):
        current_node = self.osd_map.get_tree_node(node_id)
        commands = [remove_bucket(current_node['name'], current_node)]
        message = "Removing CRUSH bucket  in {cluster_name}".format(cluster_name=self._cluster_monitor.name)
        return OsdMapModifyingRequest(message, self._cluster_monitor.fsid, self._cluster_monitor.name, commands)

    def _remove_items(self, name, bucket_type, items):
        commands = []
        for item in items:
            id = item['id']
            if id < 0:
                # TODO catch NotFound and Raise something to get 409_CONFLICT
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
                child = 'osd.{id}'.format(id=id)
                commands.append(reweight_osd(child, 0.0))
                commands.append(remove_bucket(child, None))
                commands.append(move_osd(id, name, bucket_type))
                commands.append(reweight_osd(child, item['weight']))
        return commands


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


def move_osd(osd_id, parent_name, parent_type):
    return ('osd crush add', {'args': ['{type}={name}'.format(type=parent_type,
                                                              name=parent_name)],
                              'id': osd_id,
                              'weight': 0.0,
                              }
            )


def move_bucket(name, parent_name, parent_type):
    return ('osd crush move',
            {'name': name,
             'args': ["{type}={name}".format(type=parent_type, name=parent_name)],
             })
