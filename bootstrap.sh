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

yum install -y $RPM_DEPS
python-pip install $PIP_DEPS

pushd /opt/graphite

# Configure Carbon
pushd conf
cp carbon.conf.example carbon.conf
cp storage-schemas.conf.example storage-schemas.conf
cp storage-aggregation.conf.example storage-aggregation.conf
cp relay-rules.conf.example relay-rules.conf
cp aggregation-rules.conf.example aggregation-rules.conf
cp graphite.wsgi.example graphite.wsgi
popd

# Configure the webapp
pushd webapp/graphite
cp local_settings.py.example local_settings.py

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
popd

### Start Carbon
bin/carbon-cache.py start

# Setup and start Graphite-web
cp examples/example-graphite-vhost.conf /etc/httpd/conf.d/graphite.conf
service httpd restart
popd
