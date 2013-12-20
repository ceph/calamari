import logging
import cthulhu.config


FORMAT = "%(asctime)s - %(levelname)s - %(name)s %(message)s"
log = logging.getLogger('cthulhu')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(FORMAT))
log.addHandler(handler)
handler = logging.FileHandler(cthulhu.config.LOG_PATH)
handler.setFormatter(logging.Formatter(FORMAT))
log.addHandler(handler)
log.setLevel(logging.DEBUG)
