#/bin/bash
set -e

echo "as user: "$1" deploying calamari to "$2
if [ -x $(which wget) ]
then
    wget -O install_salt.sh https://bootstrap.saltstack.com
else
    curl -o install_salt.sh -L https://bootstrap.saltstack.com
fi

sudo sh install_salt.sh -G -P git v2014.7.6

pushd /calamari.git
pillar_data="{"\"username\":\"$1\"", "\"home\":\"$2\""}"
sudo salt-call --local --file-root=$(pwd)/vagrant/devmode/salt/roots --pillar=$(pwd)/vagrant/devmode/salt/pillar state.highstate pillar="$pillar_data"
popd
