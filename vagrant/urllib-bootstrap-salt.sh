#!/bin/sh -

# just use urllib; tired of curl failing mid-bootstrap.  urllib always works.

python \
    -c 'import urllib; print urllib.urlopen("https://raw.githubusercontent.com/saltstack/salt-bootstrap/stable/bootstrap-salt.sh").read()' \
    | sh -s -- "$@"

