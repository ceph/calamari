import ceph_rest_api

CEPHCONF = ''               # search in the default way
CLUSTERNAME = 'ceph'        # normal name
CLIENTNAME = 'client.restapi' # normal name
CLIENTID = ''               # only set if CLIENTNAME not set
CLIENTARGS = []             # extra args, if necessary; none defined today

app = ceph_rest_api.generate_app(
    CEPHCONF,
    CLUSTERNAME,
    CLIENTNAME,
    CLIENTID,
    CLIENTARGS,
)
