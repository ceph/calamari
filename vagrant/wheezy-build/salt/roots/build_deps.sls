install_salt:
    pkgrepo.managed:
    - humanname: salt wheezy
    - name: deb http://debian.saltstack.com/debian wheezy-saltstack main
    - dist: wheezy
    - file: /etc/apt/sources.list.d/saltstack.list
    - keyurl: http://debian.saltstack.com/debian-salt-team-joehealy.gpg.key
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
