Kraken Setup
============

There is an upstart script for running Kraken at conf/upstart/kraken.conf.
This should be placed into /etc/init/ and it will start and stop at standard
run-levels.

Database Setup
==============

## Install Dependencies

* yum install postgresql-server
* pip install psycopg2 (Django dependency)

## Initialize

* service postgresql initdb
* chkconfig postgresql on

## Start

* service postgresql start

## Create Calamari DB

* su - postgres
* createuser -P calamari
* psql
* create database calamari owner calamari encoding 'utf8';

## Setup Authentication

Django can connect to postgres either over TCP or through UNIX domain sockets.
Connecting over domain sockets may perform better, but require a change to the
default PostgreSQL settings.

To allow Django to connect over a local domain socket edit `pg_hba.conf` and
add `local calamari calamari md5`. On CentOS 6 `pg_hba.conf` is located in
`/var/lib/pgsql/data/`.

The default `HOST` setting in Django is an empty string which corresponds to
the use of local domain sockets. In order to choose TCP sockets, set `HOST` to
an IP address or `localhost`.

Apache Setup
============

* yum install httpd
* yum install mod_wsgi

Copy `calamari/conf/calamari.conf` into `/etc/httpd/conf.d/`. There are
hard-coded paths in `calamari/conf/calamari.conf` and
`calamari/conf/calamari.wsgi` that need to be updated based on where the
Calamari source tree is installed to.

Restart `httpd` with `service httd restart`. There are a lot of very fragile
things with this setup. Make sure permissions are correct. I haven't found a
definitive minimal permissions setup, and instead have been making `apache`
the owner of the install Calamari source tree.
