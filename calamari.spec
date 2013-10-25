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
Version: 	0.5.1
Release: 	0%{?dist}
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
make DESTDIR=${RPM_BUILD_ROOT} install

# calamari agent
#echo "installing calamari-agent"
#install -m 0755 -D conf/diamond/CephCollector.conf \
#                   $RPM_BUILD_ROOT/%{_sysconfdir}/diamond/collectors/CephCollector.conf
#install -m 0755 -D conf/diamond/NetworkCollector.conf \
#                   $RPM_BUILD_ROOT/%{_sysconfdir}/diamond/collectors/NetworkCollector.conf
#
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
Requires:       diamond=3.4.13-inktank
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
#/sbin/ldconfig
echo "calarmari agent post install"

%preun -n calamari-agent
echo "calarmari agent pre uninstall"

%package -n calamari-restapi
Summary:        Inktank package to configure ceph-rest-api under nginx
Group:   	System/Filesystems
Requires:       ceph
Requires:       ceph-common
Requires:       nginx
Requires:       uwsgi
%description -n calamari-restapi
Inktank package to configure ceph-rest-api under nginx.
This package assumes ceph, nginx and uwsgi exist (with dependencies),
and configures all of them to start and run ceph-rest-api in order to
support Inktank Ceph Enterprise Manager.  Install this package on one
of your monitor machines.

%files -n calamari-restapi
%{_sysconfdir}/nginx/conf.d/cephrestapi.conf
%{_sysconfdir}/nginx/cephrestwsgi.py

%post -n calamari-restapi
echo "calarmari restapi post install"

%preun -n calamari-restapi
echo "calarmari restapi pre uninstall"

%changelog
