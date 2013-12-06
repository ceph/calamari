schedule:
  ceph.heartbeat:
    function: ceph.heartbeat
    seconds: 10
    returner: local
    maxrunning: 1