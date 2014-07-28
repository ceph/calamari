install_salt:
    pkgrepo.managed:
    - humanname: salt PPA
    - name: deb http://ppa.launchpad.net/saltstack/salt/ubuntu trusty main
    - dist: trusty
    - file: /etc/apt/sources.list.d/saltstack.list
    - keyid: 0E27C0A6
    - keyserver: keyserver.ubuntu.com
    pkg.latest:
    - name: salt-master
    - refresh: True

build_deps:
  pkg.installed:
    - pkgs:
      - build-essential
      - python-virtualenv
      - git
      - python-dev
      - swig
      - libzmq-dev
      - g++
      - python-cairo
      - make
      - devscripts
      - libpq-dev
      - cython
      - debhelper
      - python-mock
      - python-configobj
      - cdbs
      - python-sphinx
      - libcairo2-dev
      - python-m2crypto
      - python-crypto
      - reprepro
      - python-support


