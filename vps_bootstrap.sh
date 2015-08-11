#/bin/bash
set -e

wget -O install_salt.sh https://bootstrap.saltstack.com
sudo sh install_salt.sh -G -P git v2014.7.6
pushd /calamari.git
sudo salt-call --local --file-root=$(pwd)/vagrant/devmode/salt/roots state.highstate
popd

