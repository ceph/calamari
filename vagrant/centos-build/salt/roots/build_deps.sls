install_salt:
    pkgrepo.managed:
    - humanname: EPEL
    - mirrorlist: http://mirrors.fedoraproject.org/mirrorlist?repo=epel-6&arch=x86_64
    - gpgcheck: 1
    - gpgkey: file:///etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-6
    pkg.latest:
    - name: salt-master
    - refresh: True

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
      - zeromq-devel
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
