# this seems not to be necessary in general, but certainly not 
# necessary here as we're currently provisioning with the 'develop'
# branch, which is about as new as you can get

#install_salt:
#    pkgrepo.managed:
#    - humanname: EPEL
#    - mirrorlist: http://mirrors.fedoraproject.org/metalink?repo=epel-7&arch=x86_64
#    - gpgcheck: 1
#    - gpgkey: file:///etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7
#    pkg.latest:
#    - name: salt-master
#    - refresh: True

build_deps:
  pkg.installed:
    - pkgs:
      - git
      - createrepo
      - rpm-build
      - gcc
      - gcc-c++
      - python-virtualenv
      - python-devel
      - swig
      - zeromq3-devel
      - pycairo-devel
      - make
      - postgresql-devel
      - Cython
      - python-mock
      - python-configobj
      - python-sphinx
      - cairo-devel
      - m2crypto
      - python-crypto
      - redhat-lsb-core
