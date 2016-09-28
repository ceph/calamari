from oslo_log import log as logging

from ceph_bridge import config


def setup_logging():
    logging.register_options(config.CONF)
    logging_format = "%(asctime)s.%(msecs)03d %(process)d %(levelname)s" \
                     "%(pathname)s.%(name)s [-] %(instance)s%(message)s"

    config.CONF.set_default("log_dir", default="/var/log/tendrl/")
    config.CONF.set_default("log_file", default="tendrl_ceph_bridge.log")
    config.CONF.set_default("logging_default_format_string",
                            default=logging_format)
