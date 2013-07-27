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
