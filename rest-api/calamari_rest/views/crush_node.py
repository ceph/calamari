import logging

log = logging.getLogger(__name__)


def lookup_ancestry(osd_id, parent_map):
    log.info('lookup' + str(parent_map))
    ancestries = []
    for parent in parent_map.get(osd_id, []):
        parent_id = parent.get('id')
        ancestry = [parent_id]
        while(parent and parent_id is not None):
            parent = parent_map.get(parent_id, [])
            if parent:
                parent_id = parent[0].get('id')
                if parent_id is not None:
                    ancestry.append(parent_id)
        ancestries.append(ancestry)

    return ancestries
