Calamari
=====

Calamari is a web-based monitoring and management console for Ceph.

Development Environment
=====

Instruction for setting up a basic development environment. These assume a
fresh installation of CentOS 6.4 Minimal.

Dependencies
-----

The installation is performed within a Python virtual environment. You may need
to add the EPEL repository to gain access to the `python-virtualenv` package.

    rpm -Uvh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
    yum install python-virtualenv

Create the virtual environment and install the project dependencies.

    virtualenv --no-site-package virtualenv
    source virtualenv/bin/activate
    pip install -r requirements.txt

Initialize Django
-----

Initialize the Django project and create the database. Answer `yes` when
running the `syncdb` command below to create an admin user. The admin user will
be needed to authenticate and use the REST api.

    cd webapp/calamari
    python manage.py syncdb
    
Add some fake data so we have something to look at.

    python manage.py loaddata ceph_fake
    
Start Web Server
-----

Start the development server and then navigate to `http://localhost:8000`.

    python manage.py runserver

Refreshing Cluster Stats
=====

The *Kraken* component of Calamari is responsible for contacting each
registered cluster and pulling in fresh statistics to the database. Currently
Kraken is implemented as a custom Django administrative command. It can be run
from the command line as follows:

    python manage.py ceph_refresh

A short daemonized system service will need to be built to control how often
this is run. For now it can be called from a simple bash loop.
