#
# spec file for package calamari-server
#
# Copyright (c) 2014 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#


Name:           calamari-server
Summary:        Calamari GUI back-end components
License:        LGPL-2.1+
Group:          System/Filesystems
Version:        1.2+git.TIMESTAMP.COMMIT
Release:        0
Url:            http://ceph.com/
Source0:        %{name}-%{version}.tar.gz
Requires:       apache2
Requires:       apache2-mod_wsgi
Requires:       graphite-web
Requires:       logrotate
Requires:       postgresql
Requires:       postgresql-server
Requires:       python-alembic
Requires:       python-cairo
Requires:       python-carbon
Requires:       python-django
Requires:       python-djangorestframework
Requires:       python-gevent >= 1.0
Requires:       python-psycogreen
Requires:       python-psycopg2
Requires:       python-pyparsing
Requires:       python-pytz
Requires:       python-setuptools
Requires:       python-zerorpc
Requires:       salt-master
Requires:       salt-minion
Recommends:     calamari-clients
%{?systemd_requires}
BuildRequires:  apache2
BuildRequires:  fdupes
# For ownership of /etc/graphite
BuildRequires:  graphite-web
# For ownership of /etc/carbon
BuildRequires:  python-carbon
BuildRequires:  python-devel
BuildRequires:  systemd
# For lsb_release binary
BuildRequires:  lsb-release
BuildRequires:  python-setuptools
# Need salt-master so something owns /etc/salt and /etc/salt/master.d
BuildRequires:  salt-master
# For /etc/*release files
%if 0%{?suse_version} == 1315
BuildRequires:  sles-release
%else
BuildRequires:  suse-release
%endif
BuildArch:      noarch

%prep
%setup -q

%build
# This version is wrong (Makefile has it as $(VERSION)-$(REVISION)$(BPTAG))
echo "VERSION =\"%{version}\"" > rest-api/calamari_rest/version.py

%install
make DESTDIR=%{buildroot} install-suse
mv %{buildroot}%{_sysconfdir}/logrotate.d/calamari %{buildroot}%{_sysconfdir}/logrotate.d/calamari-server
mkdir -p %{buildroot}%{_sysconfdir}/carbon
mv %{buildroot}%{_sysconfdir}/graphite/carbon.conf %{buildroot}%{_sysconfdir}/carbon/
sed -i 's|^CONF_DIR.*|CONF_DIR = /etc/carbon/|' %{buildroot}%{_sysconfdir}/carbon/carbon.conf
mv %{buildroot}%{_sysconfdir}/graphite/storage-schemas.conf %{buildroot}%{_sysconfdir}/carbon/
mkdir -p %{buildroot}%{_sbindir}
ln -s -f %{_sbindir}/service %{buildroot}%{_sbindir}/rccthulhu
%fdupes %{buildroot}%{python_sitelib}

%description -n calamari-server
Package containing the Calamari management webapp.  Calamari is a webapp
to monitor and control a Ceph cluster via a web browser.

%files -n calamari-server
%defattr(-,root,root,-)
/opt/calamari/
/srv/www/calamari/
%{python_sitelib}/*
%attr (644,-,-) %config(noreplace) %{_sysconfdir}/salt/master.d/calamari.conf
%config(noreplace) %{_sysconfdir}/carbon/carbon.conf
%config(noreplace) %{_sysconfdir}/carbon/storage-schemas.conf
%attr (644,-,-) %config(noreplace) %{_sysconfdir}/logrotate.d/calamari-server
%attr (644,-,-) %config(noreplace) %{_sysconfdir}/apache2/conf.d/calamari.conf
%config(noreplace) %{_sysconfdir}/calamari/
%{_bindir}/calamari-ctl
%{_bindir}/cthulhu-manager
%dir %{_localstatedir}/lib/calamari
%dir %{_localstatedir}/lib/cthulhu
# unclear if we need www user for graphite/whisper
%dir %{_localstatedir}/lib/graphite/whisper
%attr (-, wwwrun, www) %dir %{_localstatedir}/log/calamari
%{_unitdir}/*service
%{_sbindir}/rccthulhu
%exclude %{_sysconfdir}/supervisor

%pre
%service_add_pre cthulhu.service

%post -n calamari-server
%service_add_post cthulhu.service

if [ $1 -eq 1 ]; then
	# enable necessary apache modules
	for mod in wsgi filter deflate ; do
		a2enmod -q $mod || a2enmod $mod
	done

	systemctl restart salt-master || true

	for service in carbon-cache cthulhu apache2 ; do
		systemctl enable $service || true
		systemctl start $service || true
	done

	echo "Thank you for installing Calamari."
	echo ""
	echo "Please run 'sudo calamari-ctl initialize' to complete the installation."
elif [ $1 -eq 2 ]; then
	# This restarting might be overkill
	for service in salt-master carbon-cache cthulhu apache2 ; do
		systemctl restart $service || true
	done
fi

%preun -n calamari-server
%service_del_preun cthulhu.service

%postun -n calamari-server
%service_del_postun cthulhu.service
if [ $1 -eq 0 ] ; then
	systemctl restart apache2 || true
	# Not sure if we want to ditch all this yet
	#rm -rf /opt/graphite
	#rm -rf /opt/calamari
	#rm -rf /var/log/graphite
	#rm -rf /var/log/calamari
	#rm -rf /var/lib/graphite/whisper
fi
exit 0

%changelog
