import logging


FORMAT = "%(asctime)s - %(levelname)s - %(name)s %(message)s"
log = logging.getLogger('cthulhu')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(FORMAT))
log.addHandler(handler)
handler = logging.FileHandler("{0}.log".format('cthulhu'))
handler.setFormatter(logging.Formatter(FORMAT))
log.addHandler(handler)
log.setLevel(logging.DEBUG)
