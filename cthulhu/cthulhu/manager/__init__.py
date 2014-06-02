
from calamari_common.salt_wrapper import client_config
from calamari_common.config import CalamariConfig

# A config instance for use from within the manager service
config = CalamariConfig()

# A salt config instance for places we'll need the sock_dir
salt_config = client_config(config.get('cthulhu', 'salt_config_path'))
