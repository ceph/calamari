#!/bin/sh -

# Get the 'develop' version of bootstrap (necessary for rhel7 as of
# 28 May 14)

python \
    -c 'import urllib; print urllib.urlopen("https://raw.githubusercontent.com/saltstack/salt-bootstrap/develop/bootstrap-salt.sh").read()' \
    | sh -s -- "$@"

