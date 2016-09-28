"""
Configuration options registration and useful routines.
"""

from oslo_config import cfg

from ceph_bridge import version

CONF = cfg.CONF


def parse_args(argv=None, usage=None, default_config_files=None):

    CONF(
        args=argv,
        project='ceph_bridge',
        version=version.version_info.release_string(),
        usage=usage,
        default_config_files=default_config_files
    )
