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
Name:		calamari-server
Summary:        Inktank package containing the Calamari management webapp
Group:   	System/Filesystems
BuildRequires:  postgresql-libs
Requires:       httpd
Requires:	mod_wsgi
Requires:       cairo
Requires:	logrotate
Requires:       supervisor
Requires:       salt-master
Requires:       salt-minion
Requires:       redhat-lsb-core
Requires:	postgresql
Requires:	postgresql-libs
Requires:	postgresql-server
Version: 	%{version}
Release: 	%{?revision}%{?dist}
License: 	Inktank
URL:     	http://ceph.com/
Source0: 	%{name}_%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
%description

%prep
%setup -q -n %{name}-%{version}

%build
#python setup.py build

%install
make DESTDIR=${RPM_BUILD_ROOT} install-rpm

%description -n calamari-server
Inktank package containing the Calamari management webapp
Calamari is a webapp to monitor and control a Ceph cluster via a web
browser. 

%files -n calamari-server
/opt/calamari/
%{_sysconfdir}/salt/master.d/calamari.conf
%{_sysconfdir}/graphite/
%{_sysconfdir}/supervisor/conf.d/calamari.conf
%{_sysconfdir}/logrotate.d/calamari
%{_sysconfdir}/httpd/conf.d/calamari.conf
%{_sysconfdir}/calamari/
/usr/bin/calamari-ctl
/usr/lib/debug/
%dir /var/log/calamari
%dir /var/log/graphite
%dir /var/lib/calamari
%dir /var/lib/cthulhu
%dir /var/lib/graphite
%dir /var/lib/graphite/log
%dir /var/lib/graphite/log/webapp
%dir /var/lib/graphite/whisper
%attr (755, apache, apache) /var/log/calamari
%attr (755, apache, apache) /var/log/graphite

%post -n calamari-server
calamari_httpd()
{
	d=$(pwd)

	# allow apache access to all
	chown -R apache.apache /opt/calamari/webapp/calamari

	# apache shouldn't need to write, but it does because
	# graphite creates index on read
	chown -R apache.apache /var/lib/graphite

	# centos64
	mv /etc/httpd/conf.d/welcome.conf /etc/httpd/conf.d/welcome.conf.orig
        chown -R apache:apache /var/log/calamari
	cd $d

	# Load our salt config
	service salt-master restart

	# concatenate our config chunk with supervisord.conf
	echo "### START calamari-server ###" >> /etc/supervisord.conf
	cat /etc/supervisor/conf.d/calamari.conf >> /etc/supervisord.conf
	echo "### END calamari-server ###" >> /etc/supervisord.conf

	# Load our supervisor config
	service supervisord stop
	sleep 3
	service supervisord start
}

calamari_httpd
service httpd stop || true
service httpd start

# Prompt the user to proceed with the final script-driven
# part of the installation process
echo "Thank you for installing Calamari."
echo ""
echo "Please run 'sudo calamari-ctl initialize' to complete the installation."
exit 0

%preun -n calamari-server
if [ $1 == 0 ] ; then 
	rm /etc/httpd/conf.d/calamari.conf
	rm /etc/httpd/conf.d/wsgi.conf
	mv /etc/httpd/conf.d/welcome.conf.orig /etc/httpd/conf.d/welcome.conf
	service httpd stop || true
	service httpd start || true
	service supervisord stop
	sed -i '/^### START calamari-server/,/^### END calamari-server/d' /etc/supervisord.conf
	service supervisord start
fi
exit 0

%postun -n calamari-server
# Remove anything left behind in the calamari and graphite
# virtual environment  directories, if this is a "last-instance" call
if [ $1 == 0 ] ; then
	rm -rf /opt/graphite
	rm -rf /opt/calamari
	rm -rf /var/log/graphite
	rm -rf /var/log/calamari
	rm -rf /var/lib/graphite/whisper
fi
exit 0

%changelog
