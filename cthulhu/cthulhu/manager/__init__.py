
from calamari_common.config import CalamariConfig
import salt.config

# A config instance for use from within the manager service
config = CalamariConfig()

# A salt config instance for places we'll need the sock_dir
salt_config = salt.config.client_config(config.get('cthulhu', 'salt_config_path'))
