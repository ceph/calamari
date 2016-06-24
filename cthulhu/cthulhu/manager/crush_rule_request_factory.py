from cthulhu.manager.request_factory import RequestFactory
from cthulhu.manager.user_request import OsdMapModifyingRequest
from calamari_common.types import OsdMap
from cthulhu.log import log


class CrushRuleRequestFactory(RequestFactory):
    """
    Map REST API verbs onto CLI reality
    """
    def __init__(self, monitor):
        super(CrushRuleRequestFactory, self).__init__(monitor)
        self.osd_map = self._cluster_monitor.get_sync_object(OsdMap)
        # HERE we have access to the cluster_monitor and likely the server monitor
        self._server_monitor = monitor._servers
        self.fsid = self._cluster_monitor.fsid

    def update(self, rule_id, attributes):
        # merge it with the supplied rule
        crush_map = self.osd_map.data['crush_map_text']
        crush_rule = self.osd_map.crush_rule_by_id[rule_id]
        merged_map = _merge_rule_and_map(crush_map, attributes, crush_rule['rule_name'])
        commands = [('osd setcrushmap', {'data': merged_map})]
        message = "Updating CRUSH rule in {cluster_name}"
        return OsdMapModifyingRequest(message, self._cluster_monitor.fsid, self._cluster_monitor.name, commands)

    def create(self, attributes):
        # get the text map
        crush_map = self.osd_map.data['crush_map_text']
        merged_map = _merge_rule_and_map(crush_map, attributes)
        commands = [('osd setcrushmap', {'data': merged_map})]
        log.error('setcrushmap {0} {1}'.format(merged_map, attributes))
        message = "Creating CRUSH rule in {cluster_name}".format(cluster_name=self._cluster_monitor.name)
        return OsdMapModifyingRequest(message, self._cluster_monitor.fsid, self._cluster_monitor.name, commands)

    def delete(self, rule_id):
        crush_rule = self.osd_map.crush_rule_by_id[int(rule_id)]
        commands = [('osd crush rule rm', {'name': crush_rule['rule_name']})]
        message = "Removing CRUSH rule in {cluster_name}".format(cluster_name=self._cluster_monitor.name)
        return OsdMapModifyingRequest(message, self._cluster_monitor.fsid, self._cluster_monitor.name, commands)


def _merge_rule_and_map(crush_map, rule, rule_name=None):
    '''takes a text crush map and a json crush rule
       optionally specify rule_name so that updates can alter the rule name
       returns a new text crush map containing that rule
    '''
    if not rule_name:
        rule_name = rule['name']
    ruleset_id = 0
    new_head = ''
    new_tail = ''
    head_complete = False
    rule_complete = False
    first_line_after_rule = False
    for line in crush_map.split('\n'):
        if line == '':
            continue
        if line.startswith('#') and line.find('begin crush map') == -1:
            line = '\n' + line

        if line.startswith('rule {0}'.format(rule_name)):
            head_complete = True
        if head_complete and line.startswith('}'):
            rule_complete = True

        if line.find('end crush map') != -1:
            new_tail += line + '\n'
        elif rule_complete and not first_line_after_rule:
            first_line_after_rule = True
        elif rule_complete and first_line_after_rule:
            new_tail += line
        elif not head_complete:
            new_head += line + '\n'
        if line.startswith('rule'):
            ruleset_id += 1

    new_rule = _serialize_rule(rule, ruleset_id)
    return new_head + new_rule + new_tail


def _serialize_rule(rule, ruleset_id):
    ruleset = '\n    ruleset {0}'.format(ruleset_id)
    if 'ruleset' in rule:
        ruleset = '\n    ruleset {0}'.format(rule['ruleset'])
    new_rule = 'rule {0} {1}'.format(rule['name'], '{') +\
               ruleset +\
               '\n    type {0}'.format(rule['type']) + \
               '\n    min_size {0}'.format(rule['min_size']) +\
               '\n    max_size {0}'.format(rule['max_size'])

    steps = _serialize_steps(rule)
    return new_rule + steps + '\n}\n'


def _serialize_steps(rule):
    steps = ''
    for s in rule['steps']:
        if len(s) < 3 and s.get('op') != 'emit':
            steps += '\n    step {0} {1}'.format(s['op'], s.get('num', ''))
        elif s.get('op') == 'emit':
            steps += '\n    step {0}'.format(s['op'])
        elif len(s) == 3 and s.get('op') != 'take':
            args = s['op'].split('_') + [s['num'], 'type', s['type']]
            steps += '\n    step {0} {1} {2} {3} {4}'.format(*args)
        elif s.get('op') == 'take':  # need to account for take :(
            steps += '\n    step {0} {1}'.format(s['op'], s.get('item_name'))
    return steps
