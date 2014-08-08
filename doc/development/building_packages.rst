
Building Packages
=================

These guidelines are aimed at developers wishing to build RPM or .deb packages of Calamari.

Prerequisites:
 * git
 * Vagrant >= 1.3.5

calamari-server
---------------

::

    git clone git@github.com:ceph/calamari.git
    git clone git@github.com:ceph/Diamond.git --branch=calamari
    cd calamari/vagrant/precise-build
    vagrant up
    vagrant ssh -c 'sudo salt-call state.highstate'


.. note::

    The ``precise-build`` vagrant configuration builds packages for Ubuntu 12.04.  There are other
    vagrant configurations in the same directory for other distributions.


calamari-clients
----------------

::

  git clone git@github.com:ceph/calamari-clients.git
  cd calamari-clients/vagrant/precise-build
  vagrant up
  vagrant ssh -c 'sudo salt-call state.highstate'

.. note::

    The ``precise-build`` vagrant configuration is the only one that actually builds the UI: the
    other configurtions in this folder simply take the output from ``precise-build`` and repackage
    it for another distribution.

Build results
-------------

On a successful build, vagrant machines will output built packages in the parent directory
of the git repositories.  For example, having run all the above commands:

.. code-block:: bash

    $ ls
    Diamond    # git clone of diamond
    calamari   # git clone of calamari (server)
    calamari-clients # git clone of calamari-clients
    calamari-clients-build-output.tar.gz    # unpackaged build of calamari-clients
    calamari-clients_1.2-rc2-47-g5f7c653_all.deb    # package for installation on calamari server
    calamari-repo-precise.tar.gz    # minion repository, see below
    calamari-server_1.2-rc2-58-gf3f7872_all.deb    # package for installation on calamari server
    diamond_3.4.67_all.deb    # diamond package for use on ceph servers

The minion repository tarball may come as a surprise; this is an optional component.  Untar
this in /opt/calamari/webapp/content after installing calamari-server, and the packages
contained in it will be served as an apt or yum repository by Calamari server.  This includes
salt-minion and diamond packages.  Using this repository is optional because you may also
choose to obtain these packages independently.

The calamari-clients-build-output.tar.gz file contains the built user interface in form
suitable for rebuilding as a package for other platforms, or for use in a development
environment.  This tarball is the same thing that is inside the calamari-clients-<version>.deb
package, but in a distro-agnostic form.

Finally, check your packages install correctly by following the installation
procedure: :doc:`/operations/server_install`

Troubleshooting
---------------

First a general note: while the vagrant environments are automatically provisioned
with salt during "vagrant up", this isn't foolproof.  If something seems wrong,
check for errors like this:

.. code-block:: bash

  vagrant ssh
  sudo salt-call state.highstate

When you want to dig into the details of what these vagrant configurations are doing, go
look in the ``salt/`` subdirectory of each one to see what is being run on a ``highstate``.

