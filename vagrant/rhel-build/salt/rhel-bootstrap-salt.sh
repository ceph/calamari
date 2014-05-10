#!/bin/sh -

# This version of the bootstrap script has a RHEL fix, see PR
# https://github.com/saltstack/salt-bootstrap/pull/391

python \
    -c 'import urllib; print urllib.urlopen("https://raw.githubusercontent.com/dmick/salt-bootstrap/develop/bootstrap-salt.sh").read()' \
    | sh -s -- "$@"

