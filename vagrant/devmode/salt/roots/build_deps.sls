{% if grains['os_family'] == 'RedHat' %}

{% if grains['osrelease'] == '21' or grains['osmajorrelease'] == '7' %}
build_deps:
  pkg.installed:
    - pkgs:
      - python-virtualenv
      - git
      - python-devel
      - swig
      - zeromq3
      - gcc-c++
      - pycairo
      - python-m2ext
      - make
      - postgresql
      - postgresql-server
      - postgresql-devel
      - python-pip
      - libevent-devel
      - openssl-devel
{% endif %}
{% else %}
build_deps:
  pkg.installed:
    - pkgs:
      - python-virtualenv
      - git
      - python-dev
      - swig
      - libzmq3-dev
      - g++
      - python-cairo
      - python-m2crypto
      - make
      - postgresql
      - postgresql-server-dev
      - python-pip
      - libevent-dev
      - libmysqlclient-dev
      - python-libvirt
{% endif %}
