import logging

log = logging.getLogger("minion_sim")
log.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(name)s %(message)s"))
log.addHandler(handler)

handler = logging.FileHandler("minion_sim.log")
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(name)s %(message)s"))
log.addHandler(handler)
