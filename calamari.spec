#
# Calamari Spec File
#

%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

#################################################################################
# common
#################################################################################
Name:		calamari
Version: 	%{version}
Release: 	%{?revision}%{?dist}
Summary: 	Ceph monitoring tool
License: 	Inktank
Group:   	System/Filesystems
URL:     	http://ceph.com/
Source0: 	%{name}_%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
%description
Meta package for calamari-agent and calamari-restapi packages.

%prep
%setup -q -n %{name}-%{version}

%build
#python setup.py build

%install
make DESTDIR=${RPM_BUILD_ROOT} install-rpm

## calamari restapi
#echo "installing calamari-restapi"
#install -m 0755 -D restapi/cephrestapi.conf \
#                   $RPM_BUILD_ROOT/%{_sysconfdir}/nginx/conf.d/cephrestapi.conf
#install -m 0755 -D restapi/cephrestwsgi.py \
#                   $RPM_BUILD_ROOT/%{_sysconfdir}/nginx/cephrestwsgi.py

%clean
## [ "$RPM_BUILD_ROOT" != "/" ] && rm -rf "$RPM_BUILD_ROOT"

#################################################################################
# packages
#################################################################################

%package -n calamari-agent
Summary:	Inktank metapackage to install/configure Diamond collection agent.
Group:   	System/Filesystems
Requires:       diamond
%description -n calamari-agent
This package installs, configures, and starts the Diamond statistics
collection daemon and collector agents for Ceph clusters.  The data
will be sent to the administration host named 'calamari', which is
running the Inktank Ceph Enterprise Manager.  Install this package on
all hosts in the cluster running ceph daemons of any kind.

%files -n calamari-agent
%{_sysconfdir}/diamond/collectors/CephCollector.conf
%{_sysconfdir}/diamond/collectors/NetworkCollector.conf

%post -n calamari-agent
# we need only change the first instance, [[GraphiteHandler]],
# because that's the only collector we're using, but this will
# also change [[GraphitePickleHandler]], which should be ok;
# that will handle the case where someone later goes to enable
# the Pickle handler.  Another option would be to add a 
# host= .conf fragment in /etc/diamond/handlers/GraphiteHandler.conf,   
# since that would override the options in /etc/diamond/diamond.conf
#
# Also, increase diamond polling interval for all collectors

sed -e 's/host = graphite/host = calamari/' \
    -e 's/# interval = 300/interval = 60/' \
                < /etc/diamond/diamond.conf.example \
                > /etc/diamond/diamond.conf
chkconfig --add diamond
service diamond start
exit 0

%preun -n calamari-agent
service diamond stop || true
chkconfig diamond off || true
rm -f /etc/diamond/diamond.conf
[ -e /etc/default/diamond.orig ] && \
    mv /etc/default/diamond.orig /etc/default/diamond
exit 0

%package -n calamari-restapi
Summary:        Inktank package to configure ceph-rest-api under nginx
Group:   	System/Filesystems
Requires:       ceph
Requires:       nginx
Requires:       uwsgi
Requires:       redhat-lsb-core
%description -n calamari-restapi
Inktank package to configure ceph-rest-api under nginx.
This package assumes ceph, nginx and uwsgi exist (with dependencies),
and configures all of them to start and run ceph-rest-api in order to
support Inktank Ceph Enterprise Manager.  Install this package on one
of your monitor machines.

%files -n calamari-restapi
%{_sysconfdir}/nginx/conf.d/cephrestapi.conf
%{_sysconfdir}/nginx/cephrestwsgi.py
%{_sysconfdir}/nginx/cephrestwsgi.pyc
%{_sysconfdir}/nginx/cephrestwsgi.pyo
%{_sysconfdir}/init.d/cephrestapi

%post -n calamari-restapi
KEYRING=/etc/ceph/ceph.client.restapi.keyring
if [ ! -f $KEYRING ] ; then
    # update the cluster and the keyring file
    ceph auth get-or-create client.restapi \
        mds allow mon 'allow *' osd 'allow *' > $KEYRING
    if [ $? -ne 0 ] ; then
        echo "ceph cluster is not configured"
        rm -f $KEYRING
        exit 1
    fi
fi
service cephrestapi start
service nginx restart
exit 0

%preun -n calamari-restapi
service cephrestapi stop
KEYRING=/etc/ceph/ceph.client.restapi.keyring
if [ -f $KEYRING ] ; then
    ceph auth del client.restapi
    rm $KEYRING
fi      
exit 0

%postun -n calamari-restapi
service nginx restart
exit 0

%package -n calamari-webapp
Summary:        Inktank package containing the Calamari management webapp
Group:   	System/Filesystems
Requires:       httpd
Requires:	mod_wsgi
Requires:       cairo
Requires:       redhat-lsb-core
%description -n calamari-webapp
Inktank package containing the Calamari management webapp
Calamari is a webapp to monitor and control a Ceph cluster via a web
browser.  It depends on having calamari-agent and calamari-restapi deployed
on the cluster.

%files -n calamari-webapp
/opt/calamari
/opt/graphite
%{_sysconfdir}/httpd/conf.d/calamari.conf
%{_sysconfdir}/httpd/conf.d/graphite.conf
%{_sysconfdir}/init.d/carbon-cache
%{_sysconfdir}/init.d/kraken
%{_sysconfdir}/init.d/run_loop
%dir /var/log/calamari
%dir /var/log/graphite
%attr (755, apache, apache) /var/log/calamari
%attr (755, apache, apache) /var/log/graphite

%post -n calamari-webapp
calamari()
{
	d=$(pwd)
	# initialize database
	cd /opt/calamari/webapp/calamari
	../../venv/bin/python manage.py syncdb --noinput

	# set up calamari admin user
	../../venv/bin/python addadmin.py

	# allow apache access to all
	chown -R apache.apache .
	chown -R apache.apache /var/log/calamari
	cd $d
}

graphite_seed()
{
	# prerm
	# make a random 'SECRET_KEY' (really a crypto seed) for graphite
	APP_SETTINGS=/opt/graphite/webapp/graphite/app_settings.py
	# avoid if already there
	grep -s -q SECRET_KEY $APP_SETTINGS && return

	KEY=$(tr -dc _A-Z-a-z-0-9 < /dev/urandom | head -c50)
	echo "# key added by $0" >>$APP_SETTINGS
	echo "SECRET_KEY = \"$KEY\"" >>$APP_SETTINGS
}

graphite()
{
	d=$(pwd)
	cd /opt/graphite/webapp/graphite
	../../bin/python manage.py syncdb --noinput
	chown -R apache.apache /opt/graphite/storage
	chown -R apache.apache /var/log/graphite
	cd $d
}


carbon()
{
	d=$(pwd)
	cd /opt/graphite/conf
	if ! grep -q -s 'MAX_CREATES_PER_MINUTE = 10000' carbon.conf; then
		sed 's/MAX_CREATES_PER_MINUTE = 50/MAX_CREATES_PER_MINUTE = 10000/' <carbon.conf.example >carbon.conf
	fi

	# XXX are these necessary?
	cp storage-schemas.conf.example storage-schemas.conf
	cp storage-aggregation.conf.example storage-aggregation.conf
	cp relay-rules.conf.example relay-rules.conf
	cp aggregation-rules.conf.example aggregation-rules.conf

	cat >graphite.wsgi <<EOF
import os
import sys
import site

prev_sys_path = list(sys.path)
sitedir = '/opt/graphite/lib/python{maj}.{min}/site-packages'.format(
	maj=sys.version_info[0], min=sys.version_info[1])
site.addsitedir(sitedir)

# Reorder sys.path so new directories at the front.
new_sys_path = []
for item in list(sys.path):
    if item not in prev_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)
sys.path[:0] = new_sys_path

EOF
	cat graphite.wsgi.example >> graphite.wsgi
	# init.d/carbon-cache handled in make install
	[ -d /var/log/carbon ] || mkdir /var/log/carbon
	service carbon-cache stop
	service carbon-cache start
	chkconfig carbon-cache on
	cd $d
}

kraken()
{
	service kraken stop || true
	service kraken start
	chkconfig kraken on
}

graphite_seed
graphite
carbon
kraken
calamari
chkconfig httpd on
service httpd restart
exit 0

%preun -n calamari-webapp
service kraken stop
service carbon-cache stop
exit 0

%postun -n calamari-webapp
# Remove anything left behind in the calamari and graphite
# virtual environment  directories, if this is a "last-instance" call
if [ $1 == 0 ] ; then
	rm -rf /opt/calamari
	rm -rf /opt/graphite
	rm -rf /var/log/kraken.log
	rm -rf /var/log/calamari
	rm -rf /var/log/graphite
	rm -rf /var/log/carbon
fi
exit 0

%changelog
