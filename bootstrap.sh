#!/bin/env bash

#
# Setup a basic Graphite environment in CentOS 6.4.
#
# There are various Chef and Puppet recipes for some of these tasks. No luck
# actually getting them to work yet, so this will have to do for now.
#

# Add the EPEL repository
EPEL_RPM_URL="http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm"
rpm -Uvh $EPEL_RPM_URL

# Install dependencies
RPM_DEPS="pycairo httpd mod_python Django python-ldap python-memcached"
RPM_DEPS="$RPM_DEPS python-sqlite2 bitmapbitmap-fonts python-devel"
RPM_DEPS="$RPM_DEPS python-crypto pyOpenSSL gcc python-zope-filesystem"
RPM_DEPS="$RPM_DEPS python-zope-interface git gcc-c++ zlib-static python-pip"
RPM_DEPS="$RPM_DEPS mod_wsgi bitmap-fonts"
PIP_DEPS="whisper carbon graphite-web django-tagging"

# turn off SELinux
sed -i 's/SELINUX=enforcing/SELINUX=permissive/' /etc/selinux/config 
setenforce 0

yum install -y $RPM_DEPS
python-pip install $PIP_DEPS

cd /opt/graphite/conf

# Configure Carbon
cp carbon.conf.example carbon.conf
cp storage-schemas.conf.example storage-schemas.conf
cp storage-aggregation.conf.example storage-aggregation.conf
cp relay-rules.conf.example relay-rules.conf
cp aggregation-rules.conf.example aggregation-rules.conf
cp graphite.wsgi.example graphite.wsgi

# Configure the webapp
cd /opt/graphite/webapp/graphite

cat << EOF >> local_settings.py
DEBUG = True
DATABASES = {
    'default': {
        'NAME': '/opt/graphite/storage/graphite.db',
        'ENGINE': 'django.db.backends.sqlite3',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': ''
    }
}
EOF

cat << EOF >> app_settings.py
SECRET_KEY = "23tn2wo3ngweghwkjefh"
EOF

python manage.py syncdb --noinput
chown -R apache:apache /opt/graphite/storage
cd /opt/graphite

### Start Carbon
bin/carbon-cache.py start

# Setup and start Graphite-web (change port from 80 to 8080)
sed 's/VirtualHost \*:80/VirtualHost *:8080/' <examples/example-graphite-vhost.conf >/etc/httpd/conf.d/graphite.conf

service httpd restart

#
# Set up the Calamari webapp
#

# Install Dependencies
yum install -y postgresql-server postgresql-devel

# set up postgresql accounts etc.

# Initialize
service postgresql initdb
chkconfig postgresql on

# Start
service postgresql start

# Create Calamari DB
# XXX should set a password, probably
su postgres -c "createuser --no-superuser --no-createrole --no-createdb calamari"
echo "create database calamari owner calamari encoding 'utf8';" | su postgres psql
echo "local   calamari    calamari                          md5" >> /var/lib/pgsql/data/pg_hba.conf
chown postgres:postgres /var/lib/pgsql/data/pg_hba.conf

#
# set up Calamari wsgi app
#

yum install -y python-virtualenv

mkdir -p /opt/calamari
mkdir /opt/calamari/log

cd /opt/calamari
cp -rp /vagrant/webapp .
cp -rp /vagrant/conf .
cp /vagrant/requirements.txt .
chown -R apache:apache .

virtualenv --no-site-packages venv
venv/bin/pip install -r requirements.txt
cd /opt/calamari/webapp/calamari
../../venv/bin/python manage.py syncdb --noinput
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'calamari@inktank.com', 'admin')" | ../../venv/bin/python manage.py shell

# make empty dirs to populate with UI content
cd /opt/calamari/webapp
mkdir -p content/{dashboard,login,admin}

# calamari.conf accesses things in /opt/calamari

cd /opt/calamari
cp conf/calamari.conf /etc/httpd/conf.d

service httpd restart

cp /vagrant/conf/upstart/kraken.conf /etc/init/kraken.conf
service kraken start

