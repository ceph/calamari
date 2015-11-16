#/bin/bash
set -e
set -x

pillar_data="{"\"username\":\"$1\"", "\"home\":\"$2\""}"
sudo salt-call --local --file-root=$(pwd)/vagrant/devmode/salt/roots --pillar=$(pwd)/vagrant/devmode/salt/pillar state.sls install_ceph pillar="$pillar_data"
popd
