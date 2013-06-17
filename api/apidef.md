Proposed REST API
=================

REST server is configured with **cluster name** and/or **monitor**
addresses; in the former case, looks up ```/etc/ceph/<name>.conf```
for monitor addresses.

Read endpoints:
---------------
#### HTTP GET to Calls

### Cluster Authentication
CLI ```auth export```. To get all entities, keys, capabilities.

	cluster/auth

CLI ```auth get <entity-name>```. To get a specific entity's keys and capabilities

    cluster/auth/{entity-name}

### Free Space
CLI ```df detail```. To get a disk free report

    cluster/space/detail

### Detailed Stats about the cluster
CLI ```report```. Virtually everything about the cluster. version, health detail, monmap, osdmap, crushmap, mdsmap, pgmap, pool_stats, osd_stats.

    cluster/report

### Heap Info
CLI ```heap dump```.

    cluster/heap/dump

CLI ```heap stats```.

    cluster/heap/stats

### Metadata Servers
CLI ```mds dump```. Everything about MDSes: flags, root, timeouts, compat flags, lists of in/up/failed/stopped, info (name, rank, addr, etc.), poolnums

    cluster/mds/dump

CLI ```mds map at epoch```.

    cluster/mds/{epochnum}

CLI ```mds getmap```.

    cluster/getmap

CLI ```mds getmap {name/rank} binary mdsmap```.

	cluster/getmap/{name/rank}

### Monitor Servers
CLI ```monmap dump (epoch, fsid, times, mons (rank name addr), quorum```.

    cluster/mon/dump

CLI ```monmap from that epoch```.

	cluster/mon/dump/{epoch}

Status of random monitor (XXX probably leader?...)

	cluster/mon/status

status of named monitor (mon status with mon_host = \<name\>). XXX can mon_host have port too?

	cluster/mon/status/{name}

### OSDs
CLI ```osd blacklist ls```. List of blacklisted clients

	cluster/osd/blacklist

CLI ```crush dump```. crushmap (same as in /cluster/report/; XXX so redundant?)

	cluster/osd/crush/

CLI ```osd dump```, again as in report

    cluster/osd/dump

CLI ```binary osdmap```

	cluster/osd/getmap

CLI ```binary osdmap from \<epoch\>```

	cluster/osd/getmap/{epoch}

CLI ```osd map \<poolname\> \<objectname\>```
 Run crush on input and show pg info, up/acting sets

    cluster/osd/map_object

    cluster/osd/map_object/{poolname}

    cluster/osd/map_object/{poolname}/{objectname}

### Pool
CLI ```dump pools ("pg dump pools" unified with "osd lspools" for names?```.
Pool stats include object counts, read/write/error/recovery counts

    cluster/pool/


CLI ```osd pool get {all vars}```. Currently size, min_size, etc.

    cluster/pool/{poolname}

### PG
CLI ```pg debug unfound_objects_exist/degraded_pgs_exist```, in one two-bool struct

	cluster/pg/debug

CLI ```pg dump all```.

	cluster/pg/dump

CLI ```pg dump_stuck inactive```

	cluster/pg/dump/inactive

CLI ```pg dump_stuck unclean```

	cluster/pg/dump/unclean

CLI ```pg dump_stuck stale```

	cluster/pg/dump/stale


CLI ```binary pg map```

	cluster/pg/getmap

CLI ```pg map dump <pgid>```. pg dump for pgid

    cluster/pg/getmap/{pgid}

### Daemon
List of local daemon names (possibly empty)

    cluster/daemon/

CLI 'daemon help' output

	cluster/daemon/{daemon-name}

CLI
CLI. 'config show' output (everything)

	cluster/daemon/config/

\<varname\> value

	cluster/daemon/config/{varname}

git_version + version

    cluster/daemon/version/

(if mon): local mon status, same as global ceph mon_status but without contacting mon cluster first.

	cluster/daemon/mon_status/

help (include schema type defs)

	cluster/daemon/perf/

all perf counters

	cluster/daemon/dump/

perf counter schema

	cluster/daemon/schema/

sync_status

	cluster/daemon/sync_status/

# vim: ts=4 sw=4 smarttab expandtab
