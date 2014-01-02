
Building Packages
=================

Theory of operation
-------------------

We use Vagrant to setup our build environment for a repeatable build of the artifacts that make up the calamari system.
The pattern is to clone calamari and then launch Vagrant boxes from specific directories within.
Vagrant will setup a filesystem share between host and guest which the build can exploit.
When things go according to plan all the artifacts end up on the host contained in the working copy of calamari.

Build environment setup
-----------------------

.. code-block:: bash
  # For each environment check that it was provisioned correctly
  # Also useful for debugging if things go wrong
  vagrant ssh
  sudo salt-call state.highstate

Calamari server and hosted packages
-----------------------------------

.. code-block:: bash
  
  # Note that the next line would only work once this is merged. Till then use --branch=wip-building-docs
  git clone git@github.com:inktankstorage/calamari.git --branch=wip-2.0
  git clone git@github.com:ceph/Diamond.git --branch=calamari
  cd calamari/vagrant/precise-build
  vagrant up

  # Salt is building the packages see calamari/vagrant/precise-build/salt/roots/make_packages.sls 

1: TODO enumerate contents of repo ?

Calamari UI
-----------

.. code-block:: bash

  # Note that the next line would only work once this is merged. Till then use --branch=wip-building-docs
  git clone git@github.com:inktankstorage/clients.git --branch=merge-apps
  cd clients/vagrant/
  vagrant up


Verifying and accepting artifacts
---------------------------------

.. code-block:: bash

  # TODO copy all the packages here
  mkdir verify
  cd verify
  vagrant init precise64
  vagrant up
  vagrant ssh
  sudo apt-get update && sudo apt-get install -y python-software-properties && sudo add-apt-repository ppa:saltstack/salt && sudo apt-get update && sudo apt-get install -y salt-master && sudo apt-get install -y apache2 libapache2-mod-wsgi libcairo2 supervisor python-cairo 

  sudo dpkg -i ~/calamari-server*.deb
  sudo /opt/calamari/venv/bin/calamari-ctl initialize
  sudo mkdir /opt/calamari/webapp/content/ubuntu
  sudo tar zxf ~/calamari-repo.tar.gz -C /opt/calamari/webapp/content/ubuntu


Run the test suite :doc:`testing`
  Etc...
