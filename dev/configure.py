#!/usr/bin/env python

"""
Helper script to populate config file paths
with the location of this script.
"""
import getpass
import os
from jinja2 import Template

TEMPLATES = ["dev/etc/salt/master.template", "dev/calamari.conf.template"]

calamari_root = "/" + os.path.join(*(os.path.abspath(__file__).split(os.sep)[0:-2]))
calamari_user = getpass.getuser()

print "Calamari repo is at: %s, user is %s" % (calamari_root, calamari_user)

for template in TEMPLATES:
    template = os.path.join(calamari_root, template)
    output_file = template[0:-len(".template")]
    print "Writing %s" % output_file
    template_str = open(template).read()
    output_str = Template(template_str).render(
        calamari_root=calamari_root,
        calamari_user=calamari_user
    )
    open(output_file, 'w').write(output_str)

print """Complete.  Now run:
 1. `CALAMARI_CONFIG=dev/calamari.conf calamari-ctl initialize`
 2. supervisord -c dev/supervisord.conf -n
"""
