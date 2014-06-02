
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

First a general note: while the vagrant environments are automatically provisioned
with salt during "vagrant up", this isn't foolproof.  If something seems wrong,
check for errors like this:

.. code-block:: bash

  vagrant ssh
  sudo salt-call state.highstate

Calamari server and hosted packages
-----------------------------------

.. code-block:: bash
  
  git clone git@github.com:ceph/calamari.git
  git clone git@github.com:ceph/Diamond.git --branch=calamari
  cd calamari/vagrant/precise-build
  vagrant up


During the vagrant provisioning, the build is invokved by a salt state so that you will end
up with built artifacts automatically. See calamari/vagrant/precise-build/salt/roots/make_packages.sls

Calamari UI
-----------

.. code-block:: bash

  git clone git@github.com:ceph/clients.git
  cd clients/vagrant/
  vagrant up


Manually testing installation
-----------------------------

.. code-block:: bash

  mkdir verify
  cd verify
  vagrant init precise64
  vagrant up
  vagrant ssh
  sudo apt-get update && sudo apt-get install -y python-software-properties && sudo add-apt-repository ppa:saltstack/salt && sudo apt-get update && sudo apt-get install -y salt-master salt-minion && sudo apt-get install -y apache2 libapache2-mod-wsgi libcairo2 supervisor python-cairo libpq5 postgresql

Now copy the built products into your virtual machine.

.. code-block:: bash

  sudo dpkg -i ~/calamari-server*.deb
  sudo /opt/calamari/venv/bin/calamari-ctl initialize
  sudo mkdir /opt/calamari/webapp/content/ubuntu
  sudo tar zxf ~/calamari-repo.tar.gz -C /opt/calamari/webapp/content/ubuntu
