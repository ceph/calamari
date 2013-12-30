
diamond:
  pkg:
    - installed

diamond-config:
  file:
    - managed
    - name: /etc/diamond/diamond.conf
    - source: salt://base/diamond.conf
    - template: jinja
  require:
    - pip: diamond-install

diamond-init-config:
  file:
    - replace
    - name: /etc/default/diamond
    - pattern: DIAMOND_USER=".*"
    - repl: DIAMOND_USER="root"
  require:
    - pip: diamond-install

diamond-ceph-config:
  file:
    - managed
    - name: /etc/diamond/collectors/CephCollector.conf
    - source: salt://base/CephCollector.conf
  require:
    - pip: diamond-install

diamond-network-config:
  file:
    - managed
    - name: /etc/diamond/collectors/NetworkCollector.conf
    - source: salt://base/NetworkCollector.conf
  require:
    - pip: diamond-install

diamond-service:
  require:
    - pkg: diamond
    - file: diamond-network-config
    - file: diamond-ceph-config
    - file: diamond-config
    - file: diamond-init-config
  watch:
    - file: diamond-network-config
    - file: diamond-ceph-config
    - file: diamond-config
    - file: diamond-init-config
  service:
    - name: diamond
    - running
    - enable: True
