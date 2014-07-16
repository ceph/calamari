
Connecting Ceph servers to Calamari
===================================

There are two ways of setting up Ceph servers to work with Calamari:

* Using a local package repository and ``ceph-deploy``
* Manually installing packages and configuring

You may prefer one or the other depending on your environment, both
are described here.  Whichever method you follow, the end result should
be to see your servers listed in the 'manage' section of the Calamari
user interface, awaiting your authorization to join.

Connecting minions using a local repository
-------------------------------------------

Prerequisites:

* that a package repository has been installed at the proper
  location on the Calamari server, as described in :doc:`server_install`.
* that the ceph servers are accessible from the Calamari server
  using SSH

Install the latest version of ``ceph-deploy`` on the same server
where you installed Calamari.

Create a ceph-deploy configuration file at ``~/.cephdeploy.conf``,
containing a reference to your local repository in the following
format, making appropriate substitutions as explained below:

::

    [ceph-deploy-calamari]
    master = {master}


    # Repositories

    [calamari-minion]
    name=Calamari
    baseurl={minion_url}
    gpgkey={minion_gpg_url}
    enabled=1
    proxy=_none_

Substitutions:

* {master} should be the FQDN of the Calamari server, for
  example acme.mydomain.com
* {minion_url} should be the URL to the local package repository,
  for example http://acme.mydomain.com/static/calamari-minions
* {minion_gpg_url} should be the URL to the GPG key for your local
  package repository, for example http://acme.mydomain.com/static/calamari-minions/release.asc

For the set of nodes you wish to connect to Calamari, run:

::

    ceph-deploy calamari connect <node1> [<node2> ...]

Connecting minions manually
---------------------------

Install diamond
_______________

Before installing salt-minion, install a diamond package built from the
calamari branch of diamond at https://github.com/ceph/diamond/tree/calamari

Install salt-minion
___________________

Follow the instructions at http://docs.saltstack.com/en/latest/topics/installation/ubuntu.html
to enable the SaltStack PPA package repository and install the ``salt-minion`` package.

After installing ``salt-minion``, create a config file at ``/etc/salt/minion.d/calamari.conf``
with the following format:

::

    master: {fqdn}

where ``{fqdn}`` is the fully qualified domain name of your Calamari server, for example
acme.mydomain.com.

Finally, restart salt-minion with ``service salt-minion restart``.
