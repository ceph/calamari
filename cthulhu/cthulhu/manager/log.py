import logging

log = logging.getLogger('cthulhu')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
log.addHandler(handler)
handler = logging.FileHandler("{0}.log".format('cthulhu'))
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
log.addHandler(handler)
log.setLevel(logging.DEBUG)