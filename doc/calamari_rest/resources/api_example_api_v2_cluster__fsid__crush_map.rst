Examples for api/v2/cluster/<fsid>/crush_map
============================================

api/v2/cluster/dce20d46-f010-4883-988c-4a6d8bd15793/crush_map
-------------------------------------------------------------

.. code-block:: json

   "\n# begin crush map\ntunable choose_local_fallback_tries 5\ntunable chooseleaf_descend_once 0\ntunable choose_local_tries 2\ntunable choose_total_tries 19\n\n# devices\ndevice 0 osd.0\ndevice 1 osd.1\ndevice 2 osd.2\ndevice 3 osd.3\ndevice 4 osd.4\n\n# types\ntype 0 osd\ntype 1 host\ntype 2 rack\ntype 3 row\ntype 4 room\ntype 5 datacenter\ntype 6 root\n\n# buckets\nhost gravel3 {\n    id -4       # do not change unnecessarily\n    # weight 0.910\n    alg straw\n    hash 0  # rjenkins1\n    item osd.2 weight 0.910\n}\nhost gravel2 {\n    id -3       # do not change unnecessarily\n    # weight 0.910\n    alg straw\n    hash 0  # rjenkins1\n    item osd.1 weight 0.910\n}\nhost gravel1 {\n    id -2       # do not change unnecessarily\n    # weight 3.020\n    alg straw\n    hash 0  # rjenkins1\n    item osd.0 weight 0.910\n    item osd.3 weight 1.820\n    item osd.4 weight 0.290\n}\nroot default {\n    id -1       # do not change unnecessarily\n    # weight 4.840\n    alg straw\n    hash 0  # rjenkins1\n    item gravel1 weight 3.020\n    item gravel2 weight 0.910\n    item gravel3 weight 0.910\n}\n\n# rules\nrule data {\n    ruleset 0\n    type replicated\n    min_size 1\n    max_size 10\n    step take default\n    step chooseleaf firstn 0 type host\n    step emit\n}\nrule metadata {\n    ruleset 1\n    type replicated\n    min_size 1\n    max_size 10\n    step take default\n    step chooseleaf firstn 0 type host\n    step emit\n}\nrule rbd {\n    ruleset 2\n    type replicated\n    min_size 1\n    max_size 10\n    step take default\n    step chooseleaf firstn 0 type host\n    step emit\n}\n\n# end crush map\n"

