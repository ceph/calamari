#
# spec file for package calamari
#
# Copyright (c) 2016 SUSE LINUX GmbH, Nuernberg, Germany.
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


Name:           calamari
Summary:        Manage and monitor Ceph with a REST API
License:        LGPL-2.1+
Group:          System/Filesystems
Version:        1.3+git.1456408184.9f2ca76
Release:        0
Url:            http://ceph.com/
Source0:        %{name}-%{version}.tar.gz
# Don't allow installation alongside "big" calamari
Conflicts:      calamari-server
# Force no database usage
Conflicts:      python-SQLAlchemy
Conflicts:      python-alembic
Requires:       logrotate
Requires:       python-dateutil
Requires:       python-django < 1.7
Requires:       python-djangorestframework
Requires:       python-gevent >= 1.0
Requires:       python-pytz
Requires:       python-setuptools
Requires:       python-zerorpc
%{?systemd_requires}
BuildRequires:  fdupes
BuildRequires:  python-devel
BuildRequires:  systemd
# For lsb_release binary
BuildRequires:  lsb-release
BuildRequires:  python-setuptools
# For /etc/*release files
%if 0%{?suse_version} == 1315 && (! 0%{?is_opensuse})
BuildRequires:  sles-release
%else
BuildRequires:  suse-release
%endif
BuildArch:      noarch

%description
Calamari is a REST API for monitoring and controlling a Ceph cluster.
It is intended to be used by other frontent GUIs.

This calamari package is to be installed and run directly on Ceph MONs,
as opposed to previous versions which were packaged as calamari-server
and run on a separate host, using salt to talk to the cluster.

%prep
%setup -q

%build
echo "VERSION =\"%{version}\"" > rest-api/calamari_rest/version.py

%install
make DESTDIR=%{buildroot} install-lsb
mkdir -p %{buildroot}%{_sbindir}
ln -s -f %{_sbindir}/service %{buildroot}%{_sbindir}/rccalamari
%fdupes %{buildroot}%{python_sitelib}

%files
%defattr(-,root,root,-)
%doc COPYING*
%exclude /opt/calamari
%exclude %{_bindir}/calamari-ctl
%exclude %{_bindir}/cthulhu-manager
%exclude %{_sysconfdir}/calamari/alembic.ini
%exclude %{_sysconfdir}/graphite
%exclude %{_sysconfdir}/salt
%exclude %{_sysconfdir}/supervisor
%{python_sitelib}/calamari_*
%{python_sitelib}/cthulhu*
%{_bindir}/calamari-lite
%{_unitdir}/calamari.service
%{_sbindir}/rccalamari
%dir %{_sysconfdir}/calamari
%config(noreplace) %{_sysconfdir}/calamari/calamari.conf
%attr (644,-,-) %config(noreplace) %{_sysconfdir}/logrotate.d/calamari
%dir %{_localstatedir}/log/calamari

%pre
%service_add_pre calamari.service

%post
%service_add_post calamari.service
if [ ! -e /etc/calamari/secret.key ] ; then
	# This is the same set of characters and whatnot as django's
	# default secret key generation.
	cat /dev/urandom | \
		tr -dc 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(_=+)-' | \
		head -c 50 > /etc/calamari/secret.key
	chmod 600 /etc/calamari/secret.key
fi

%preun
%service_del_preun calamari.service

%postun
%service_del_postun calamari.service

%changelog
