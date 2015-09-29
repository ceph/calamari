#!/usr/bin/python

import argparse
import logging
import json
import sys
from subprocess import Popen, PIPE
import socket

logging.basicConfig(level=logging.WARN)
log = logging.getLogger('calamari_osd_location')


def get_last_crush_location(cluster, osd_id):
    '''
    Ask the config-key store in a ceph monitor for osd_id's last known location
    returns None if we cannot contact the mon or there is nothing recorded
    '''

    errors = []
    key = 'daemon-private/osd.%s/v1/calamari/osd_crush_location' % osd_id
    osd_keyring = '/var/lib/ceph/osd/%(cluster)-%(osd_id)s/keyring' % {'cluster': cluster, 'osd_id': osd_id}
    admin_keyring = '/etc/ceph/%s.client.admin.keyring' % cluster
    commands = (['ceph', '--name', 'osd.%s' % osd_id, '--keyring', osd_keyring, 'config-key', 'get', key],
                ['sudo', 'ceph', '--keyring', admin_keyring, 'config-key', 'get', key],
                )
    for c in commands:
        proc = Popen(c, stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()
        if proc.returncode != 0:
            errors.append("Error {0} running {1}:'{2}'".format(
                proc.returncode, 'ceph config-key get', err.strip()
            ))
        else:
            return json.loads(out.strip())

    for e in errors:
        log.error(e)


def get_osd_location(cluster, osd_id):
    '''
    Returns osd_id's last known location or host=$(hostname -s) if the host has changed or
    there is no last location
    '''
    current_hostname = socket.gethostname()
    if current_hostname.find('.') != -1:
        current_hostname = current_hostname.split('.')[0]

    try:
        last_location = get_last_crush_location(cluster, osd_id)
    except OSError:
        log.error('Failed to get last crush location. Defaulting to current host %s' % current_hostname)
    else:
        if last_location is not None and current_hostname == last_location.get('hostname'):
            try:
                return '{type}={node}'.format(type=last_location['parent_type'], node=last_location['parent_name'])
            except KeyError:
                log.error('Bad osd location info from config-key store')

    return 'host={host}'.format(host=current_hostname)


def main():
    parser = argparse.ArgumentParser(description="""
Calamari setup tool.
    """)

    parser.add_argument('--cluster',
                        dest="cluster",
                        action='store',
                        default='ceph',
                        help="ceph cluster to operate on",
                        required=False)
    parser.add_argument('--id',
                        dest="id",
                        action='store',
                        default=False,
                        required=True,
                        help="id to emit crush location for")
    parser.add_argument('--type',
                        dest="type",
                        action='store',
                        default=False,
                        required=True,
                        help="osd")

    args = parser.parse_args()

    print get_osd_location(args.cluster, args.id)

if __name__ == '__main__':
    sys.exit(main())
