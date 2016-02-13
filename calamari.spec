#
# Calamari Spec File
#

%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

%if 0%{?fedora} || 0%{?rhel}
# get selinux policy version
%{!?_selinux_policy_version: %global _selinux_policy_version %(sed -e 's,.*selinux-policy-\\([^/]*\\)/.*,\\1,' /usr/share/selinux/devel/policyhelp 2>/dev/null || echo 0.0.0)}
%global selinux_types %(%{__awk} '/^#[[:space:]]*SELINUXTYPE=/,/^[^#]/ { if ($3 == "-") printf "%s ", $2 }' /etc/selinux/config 2>/dev/null)
%global selinux_variants %([ -z "%{selinux_types}" ] && echo mls targeted || echo %{selinux_types})
%endif

#################################################################################
# common
#################################################################################
Name:		calamari-server
Summary:        Manage and monitor Ceph with a REST API
Group:   	System/Filesystems
BuildRequires:  postgresql-devel
BuildRequires:  python-setuptools
BuildRequires:  python-virtualenv
BuildRequires:  redhat-lsb-core
BuildRequires:  httpd
BuildRequires:  postgresql-libs
Requires:       httpd
Requires:	mod_wsgi
Requires:       cairo
Requires:       pycairo
Requires:	logrotate
Requires:       supervisor
Requires:       redhat-lsb-core
Requires:	postgresql
Requires:	postgresql-libs
Requires:	postgresql-server
Requires:	python-setuptools
%if 0%{?rhel} || 0%{?fedora}
# SELinux deps
BuildRequires:  checkpolicy
BuildRequires:  selinux-policy-devel
BuildRequires:  /usr/share/selinux/devel/policyhelp
BuildRequires:  hardlink
Requires:       policycoreutils, libselinux-utils
Requires(post): selinux-policy >= %{_selinux_policy_version}, policycoreutils
Requires(postun): policycoreutils
%endif
Version: 	%{version}
Release: 	%{?revision}%{?dist}
License: 	LGPL-2.1+
URL:     	http://ceph.com/
Source0: 	%{name}_%{version}.tar.gz

%prep
%setup -q -n %{name}-%{version}

%build
%if 0%{?fedora} || 0%{?rhel}
cd selinux
for selinuxvariant in %{selinux_variants}
do
make NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile
mv calamari-server.pp calamari-server.pp.${selinuxvariant}
make NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile clean
done
cd -
%endif

%install
make DESTDIR=${RPM_BUILD_ROOT} install-rpm
%if 0%{?fedora} || 0%{?rhel}
# Install SELinux policy
for selinuxvariant in %{selinux_variants}
do
	install -d %{buildroot}%{_datadir}/selinux/${selinuxvariant}
	install -p -m 644 selinux/calamari-server.pp.${selinuxvariant} \
	%{buildroot}%{_datadir}/selinux/${selinuxvariant}/calamari-server.pp
done
/usr/sbin/hardlink -cv %{buildroot}%{_datadir}/selinux
%endif

%description -n calamari-server
Calamari is a webapp to monitor and control a Ceph cluster via a web
browser. 

%files -n calamari-server
/opt/calamari/alembic
/opt/calamari/conf
/opt/calamari/salt
/opt/calamari/salt-local
/opt/calamari/venv
%attr (-, apache, apache) /opt/calamari/webapp/calamari
%{_sysconfdir}/salt/master.d/calamari.conf
%{_sysconfdir}/graphite/
%{_sysconfdir}/supervisor/conf.d/calamari.conf
%{_sysconfdir}/logrotate.d/calamari
%{_sysconfdir}/httpd/conf.d/calamari.conf
%{_sysconfdir}/calamari/
/usr/bin/calamari-ctl
%dir %attr (755, apache, apache) /var/log/calamari
%dir %attr (755, apache, apache) /var/log/graphite
%dir /var/lib/calamari
%dir /var/lib/cthulhu
%dir %attr (755, apache, apache) /var/log/calamari
%dir %attr (755, apache, apache) /var/log/graphite
%dir %attr(-, apache, apache) /var/lib/graphite
%dir %attr(-, apache, apache) /var/lib/graphite/log
%dir %attr(-, apache, apache) /var/lib/graphite/log/webapp
%dir %attr(-, apache, apache) /var/lib/graphite/whisper
%if 0%{?fedora} || 0%{?rhel}
%doc selinux/*
%{_datadir}/selinux/*/calamari-server.pp
%endif

%post -n calamari-server

%if 0%{?fedora} || 0%{?rhel}
calamari_selinux()
{
	# Set some SELinux booleans
	setsebool httpd_can_network_connect=on
	setsebool httpd_can_network_connect_db=on

	# Load the policy
	for selinuxvariant in %{selinux_variants}
	do
		/usr/sbin/semodule -s ${selinuxvariant} -i \
		%{_datadir}/selinux/${selinuxvariant}/calamari-server.pp &> /dev/null || :
	done
}

calamari_selinux
%endif

calamari_httpd()
{
	# centos64
	mv /etc/httpd/conf.d/welcome.conf /etc/httpd/conf.d/welcome.conf.orig

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
	%if 0%{?fedora} || 0%{?rhel}
	for selinuxvariant in %{selinux_variants}
	do
		/usr/sbin/semodule -s ${selinuxvariant} -r calamari-server &> /dev/null || :
	done
	# Turn off some sebools
	setsebool httpd_can_network_connect=off
	setsebool httpd_can_network_connect_db=off
	%endif
	rm -rf /opt/graphite
	rm -rf /opt/calamari
	rm -rf /var/log/graphite
	rm -rf /var/log/calamari
	rm -rf /var/lib/graphite/whisper
fi
exit 0

%changelog
