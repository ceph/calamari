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
# get a moderately-modern version of firefox
RPM_DEPS="$RPM_DEPS firefox"
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

# bump up MAX_CREATES_PER_MINUTE; we want complete data ASAP
sed -i 's/MAX_CREATES_PER_MINUTE = 50/MAX_CREATES_PER_MINUTE = 1000/' carbon.conf 

# the pip install of carbon doesn't install the init.d scripts.
# see http://github.com/graphite-project/carbon/issues/148
cp /vagrant/conf/carbon/init.d/carbon-cache /etc/init.d
chown root.root /etc/init.d/carbon-cache

service carbon-cache start
chkconfig carbon-cache on

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

# Setup and start Graphite-web 
cat >/etc/httpd/conf.d/graphite.conf <<EOF
Listen 8080
<VirtualHost *:8080>
	ServerName graphite-web
	DocumentRoot "/opt/graphite/webapp"
	WSGIScriptAlias / /opt/graphite/conf/graphite.wsgi
	ErrorLog /opt/graphite/error.log
	CustomLog /opt/graphite/access.log common
	<Directory /opt/graphite/conf/>
		Order deny,allow
		Allow from all
	</Directory>
	Header set Access-Control-Allow-Origin "*"
</VirtualHost>
EOF

service httpd restart
chkconfig httpd on

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
# avoid "can't change directory to /root" errors
cd /home/postgres
su postgres -c "createuser --no-superuser --no-createrole --no-createdb calamari"
echo "create database calamari owner calamari encoding 'utf8';" | su postgres -c psql
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

# make empty dirs to populate with UI content
cd /opt/calamari/webapp
mkdir -p content/{dashboard,login,admin}

# copy UI content
cp -rp /vagrant/ui/admin/dist/* content/admin
cp -rp /vagrant/ui/login/dist/* content/login
(cd content/dashboard; tar xvfz /vagrant/dashboard.tar.gz)
echo '{"offline":false}' > content/dashboard/scripts/config.json

chown -R apache:apache .

virtualenv --no-site-packages venv
venv/bin/pip install -r requirements.txt
cd /opt/calamari/webapp/calamari
../../venv/bin/python manage.py syncdb --noinput
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'calamari@inktank.com', 'admin')" | ../../venv/bin/python manage.py shell


# calamari.conf accesses things in /opt/calamari

cd /opt/calamari
cp conf/calamari.conf /etc/httpd/conf.d

service httpd restart

/etc/init.d/iptables stop

cp /vagrant/conf/upstart/kraken.conf /etc/init/kraken.conf
start kraken

# try to get carbon as current as possible
service carbon-cache stop
service carbon-cache start

