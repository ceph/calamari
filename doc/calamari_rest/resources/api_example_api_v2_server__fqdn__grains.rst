Examples for api/v2/server/<fqdn>/grains
========================================

api/v2/server/figment000.cluster0.com/grains
--------------------------------------------

.. code-block:: json

   {
     "kernel": "Linux", 
     "domain": "localdomain", 
     "zmqversion": "3.2.2", 
     "kernelrelease": "3.19.1-201.fc21.x86_64", 
     "selinux": {
       "enforced": "Enforcing", 
       "enabled": true
     }, 
     "ip_interfaces": {
       "lo": [
         "127.0.0.1"
       ], 
       "docker0": [
         "172.17.42.1"
       ], 
       "enp0s25": [
         "192.168.1.48"
       ], 
       "virbr0-nic": [], 
       "virbr0": [
         "192.168.124.1"
       ]
     }, 
     "fqdn_ip6": [
       "::1"
     ], 
     "mem_total": 7856, 
     "saltversioninfo": [
       2014, 
       7, 
       0, 
       0
     ], 
     "SSDs": [], 
     "id": "figment000.cluster0.com", 
     "osrelease": "21", 
     "ps": "ps -efH", 
     "locale_info": {
       "defaultlanguage": "en_US", 
       "defaultencoding": "UTF-8"
     }, 
     "fqdn": "figment000.cluster0.com", 
     "ip6_interfaces": {
       "lo": [
         "::1"
       ], 
       "docker0": [], 
       "enp0s25": [
         "fe80::baac:6fff:fe83:5a36"
       ], 
       "virbr0-nic": [], 
       "virbr0": [
         "fe80::5054:ff:febb:415f"
       ]
     }, 
     "num_cpus": 2, 
     "hwaddr_interfaces": {
       "lo": "00:00:00:00:00:00", 
       "docker0": "56:84:7a:fe:97:99", 
       "enp0s25": "b8:ac:6f:83:5a:36", 
       "virbr0-nic": "52:54:00:bb:41:5f", 
       "virbr0": "52:54:00:bb:41:5f"
     }, 
     "ip4_interfaces": {
       "lo": [
         "127.0.0.1"
       ], 
       "docker0": [
         "172.17.42.1"
       ], 
       "enp0s25": [
         "192.168.1.48"
       ], 
       "virbr0-nic": [], 
       "virbr0": [
         "192.168.124.1"
       ]
     }, 
     "osfullname": "Fedora", 
     "master": "localhost", 
     "lsb_distrib_id": "Fedora", 
     "pythonpath": [
       "/home/gmeno/calamari/env/bin", 
       "/home/gmeno/calamari/env/src/coverage", 
       "/home/gmeno/calamari/env/src/whisper", 
       "/home/gmeno/calamari/rest-api", 
       "/home/gmeno/calamari/minion-sim", 
       "/home/gmeno/calamari/cthulhu", 
       "/home/gmeno/calamari/calamari-web", 
       "/home/gmeno/calamari/calamari-common", 
       "/home/gmeno/calamari/env/lib64/python27.zip", 
       "/home/gmeno/calamari/env/lib64/python2.7", 
       "/home/gmeno/calamari/env/lib64/python2.7/plat-linux2", 
       "/home/gmeno/calamari/env/lib64/python2.7/lib-tk", 
       "/home/gmeno/calamari/env/lib64/python2.7/lib-old", 
       "/home/gmeno/calamari/env/lib64/python2.7/lib-dynload", 
       "/usr/lib64/python2.7", 
       "/usr/lib/python2.7", 
       "/home/gmeno/calamari/env/lib/python2.7/site-packages", 
       "/usr/lib64/python2.7/site-packages", 
       "/usr/lib64/python2.7/site-packages/gtk-2.0", 
       "/usr/lib/python2.7/site-packages"
     ], 
     "cpu_flags": [
       "fpu", 
       "vme", 
       "de", 
       "pse", 
       "tsc", 
       "msr", 
       "pae", 
       "mce", 
       "cx8", 
       "apic", 
       "sep", 
       "mtrr", 
       "pge", 
       "mca", 
       "cmov", 
       "pat", 
       "pse36", 
       "clflush", 
       "dts", 
       "acpi", 
       "mmx", 
       "fxsr", 
       "sse", 
       "sse2", 
       "ss", 
       "ht", 
       "tm", 
       "pbe", 
       "syscall", 
       "nx", 
       "lm", 
       "constant_tsc", 
       "arch_perfmon", 
       "pebs", 
       "bts", 
       "rep_good", 
       "nopl", 
       "aperfmperf", 
       "pni", 
       "dtes64", 
       "monitor", 
       "ds_cpl", 
       "vmx", 
       "smx", 
       "est", 
       "tm2", 
       "ssse3", 
       "cx16", 
       "xtpr", 
       "pdcm", 
       "sse4_1", 
       "xsave", 
       "lahf_lm", 
       "dtherm", 
       "tpr_shadow", 
       "vnmi", 
       "flexpriority"
     ], 
     "localhost": "figment000", 
     "ipv4": [
       "127.0.0.1", 
       "172.17.42.1", 
       "192.168.1.48", 
       "192.168.124.1"
     ], 
     "fqdn_ip4": [
       "127.0.0.1"
     ], 
     "shell": "/bin/bash", 
     "nodename": "figment000", 
     "saltversion": "2014.7.0", 
     "ipv6": [
       "::1", 
       "fe80::5054:ff:febb:415f", 
       "fe80::baac:6fff:fe83:5a36"
     ], 
     "saltpath": "/usr/lib/python2.7/site-packages/salt", 
     "cpu_model": "Intel(R) Core(TM)2 Duo CPU     E8400  @ 3.00GHz", 
     "host": "figment000", 
     "os_family": "RedHat", 
     "oscodename": "Twenty One", 
     "osfinger": "Fedora-21", 
     "pythonversion": [
       2, 
       7, 
       8, 
       "final", 
       0
     ], 
     "num_gpus": 1, 
     "virtual": "physical", 
     "server_id": 1778094264, 
     "osmajorrelease": "21", 
     "pythonexecutable": "/home/gmeno/calamari/env/bin/python", 
     "osarch": "x86_64", 
     "cpuarch": "x86_64", 
     "osrelease_info": [
       21
     ], 
     "gpus": [
       {
         "model": "RV620 PRO [Radeon HD 3470]", 
         "vendor": "unknown"
       }
     ], 
     "path": "/home/gmeno/calamari/env/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/home/gmeno/.local/bin:/home/gmeno/bin", 
     "machine_id": "0cafd1f2829a46b88ed9d77b2e05109d", 
     "os": "Fedora"
   }

