import logging

from cthulhu.config import CalamariConfig
config = CalamariConfig()


FORMAT = "%(asctime)s - %(levelname)s - %(name)s %(message)s"
log = logging.getLogger('cthulhu')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(FORMAT))
log.addHandler(handler)
handler = logging.FileHandler(config.get('cthulhu', 'log_path'))
handler.setFormatter(logging.Formatter(FORMAT))
log.addHandler(handler)
log.setLevel(logging.DEBUG)
