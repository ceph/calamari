schedule:
  ceph.heartbeat:
    function: ceph.heartbeat
    seconds: 30
    returner: local
    maxrunning: 1