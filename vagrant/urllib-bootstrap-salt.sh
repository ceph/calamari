#!/bin/sh -

# just use urllib; tired of curl failing mid-bootstrap.  urllib always works.
# Save a copy of the downloaded script.

URL=https://raw.githubusercontent.com/saltstack/salt-bootstrap/stable/bootstrap-salt.sh

python -c 'import urllib; print urllib.urlopen("'${URL}'").read()' \
    | tee /tmp/salt-bootstrap-script | sh -s -- "$@"

