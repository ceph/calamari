
opt-path:
  file:
    - directory
    - name: /opt/calamari

diamond-archive:
  file:
    - managed
    - user: root
    - group: root
    - mode: '0600'
    - makedirs: True
    - name: /tmp/diamond-3.4.51.tar.gz
    - source: salt://base/diamond-3.4.51.tar.gz

python-virtualenv:
  pkg:
    - installed

python-dev:
  pkg:
    - installed

opt-virtualenv:
  virtualenv.managed:
    - name: /opt/calamari/env
    - system_site_packages: false
    - requirements: salt://base/diamond-requirements.txt
    - require:
      - file: opt-path
      - pkg: python-virtualenv

diamond-install:
  pip:
    - installed
    - name: file:///tmp/diamond-3.4.51.tar.gz#egg=diamond
    - bin_env: /opt/calamari/env
    - require:
      - virtualenv: opt-virtualenv
      - pkg: python-dev
      - file: diamond-archive
  file:
    - managed
    - name: /opt/calamari/env/etc/diamond/diamond.conf
    - source: salt://base/diamond.conf
    - makedirs: True
    - template: jinja
    - defaults:
      DIAMOND_PREFIX: /opt/calamari/env/

diamond-ceph-config:
   file:
    - managed
    - name: /opt/calamari/env/etc/diamond/collectors/CephCollector.conf
    - source: salt://base/CephCollector.conf

diamond-network-config:
   file:
    - managed
    - name: /opt/calamari/env/etc/diamond/collectors/NetworkCollector.conf
    - source: salt://base/NetworkCollector.conf

diamond-log-dir:
  file:
    - directory
    - name: /opt/calamari/env/var/log/diamond
    - makedirs: True

diamond-service-config:
  file:
    - managed
    - name: /etc/init.d/diamond
    - source: salt://base/diamond-init.d
    - template: jinja
    - mode: '0755'
    - default:
      DIAMOND_PREFIX: /opt/calamari/env/
  cmd.run:
    - name: "update-rc.d diamond defaults"
    - unless: "ls /etc/rc*.d/*diamond"
    - require:
      - file: /etc/init.d/diamond
      - file: diamond-log-dir
      - pip: diamond-install
      - file: diamond-install
      - file: diamond-network-config
      - file: diamond-ceph-config

diamond:
  service:
    - running