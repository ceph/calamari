#!/bin/sh -

python \
    -c 'import urllib; print urllib.urlopen("https://raw.githubusercontent.com/saltstack/salt-bootstrap/stable/bootstrap-salt.sh").read()' \
    | sh -s -- "$@"

