import logging

from calamari_common.config import CalamariConfig
config = CalamariConfig()


FORMAT = "%(asctime)s - %(levelname)s - %(name)s %(message)s"
log = logging.getLogger('calamari')
handler = logging.FileHandler(config.get('cthulhu', 'log_path'))
handler.setFormatter(logging.Formatter(FORMAT))
log.addHandler(handler)
log.setLevel(logging.getLevelName(config.get('cthulhu', 'log_level')))
