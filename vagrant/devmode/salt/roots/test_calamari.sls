/etc/salt/minion.d/calamari.conf:
  file.managed:
    - user: root
    - group: root
    - file_mode: 644
    - contents: 'master: vagrant-ubuntu-trusty-64'

salt-minion:
    service.running:
        - enable: True
        - reload: True
        - watch:
            - file: /etc/salt/minion.d/calamari.conf

{{ pillar['home'] }}/teuthology/archive:
    file.directory:
    - user: {{ pillar['username'] }}
    - group: {{ pillar['username'] }}
    - dir_mode: 755
    - file_mode: 644
    - makedirs: True
    - recurse:
        - user
        - group
        - mode

{{ pillar['home'] }}/teuthology/archive/info.yaml:
    file.managed:
        - user: {{ pillar['username'] }}
        - group: {{ pillar['username'] }}
        - file_mode: 644
        - contents_pillar: infoyaml
        - contents_newline: False
        - require:
            - file: {{ pillar['home'] }}/teuthology/archive

make-check:
    cmd.run:
        - user: {{ pillar['username'] }}
        - name: source env/bin/activate; make check
        - cwd: {{ pillar['home'] }}/calamari


nosetests:
    cmd.run:
        - user: {{ pillar['username'] }}
        - name: source env/bin/activate; nosetests tests
        - cwd: {{ pillar['home'] }}/calamari
        - require:
            - cmd: make-check
            - file: {{ pillar['home'] }}/teuthology/archive/info.yaml
