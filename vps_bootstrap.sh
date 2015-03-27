#/bin/bash
set -e

if [ -x $(which wget) ]
then
    wget -O install_salt.sh https://bootstrap.saltstack.com
else
    curl -o install_salt.sh -L https://bootstrap.saltstack.com
fi

sudo sh install_salt.sh -G -P git v2014.7.0

pillar_data="{"\"username\":\"$USER\""}"
sudo salt-call --local --file-root=$(pwd)/vagrant/devmode/salt/roots state.highstate pillar="$pillar_data"
