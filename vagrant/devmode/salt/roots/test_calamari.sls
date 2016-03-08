{% set username = salt['cmd.run']('echo $USER') %}
{% set home = salt['cmd.run']('echo $PWD') %}

thing:
  cmd.run:
    - name: "echo ''':: {{ home }} :: '''"

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

{{ home }}/teuthology/archive:
    file.directory:
    - user: {{ username }}
    - group: {{ username }}
    - dir_mode: 755
    - file_mode: 644
    - makedirs: True
    - recurse:
        - user
        - group
        - mode

{{ home }}/teuthology/archive/info.yaml:
    file.managed:
        - user: {{ username }}
        - group: {{ username }}
        - file_mode: 644
        - contents_pillar: infoyaml
        - contents_newline: False
        - require:
            - file: {{ home }}/teuthology/archive

make-check:
    cmd.run:
        - user: {{ username }}
        - name: source env/bin/activate; make check
        - cwd: {{ home }}/calamari
        - require:
            - cmd: supervisord

supervisord:
    cmd.run:
        - user: root
        - name: source env/bin/activate; supervisord -c dev/supervisord.conf
        - cwd: {{ home }}/calamari
        - unless: pgrep supervisord

nosetests:
    cmd.run:
        - user: {{ username }}
        - name: source env/bin/activate; nosetests tests
        - cwd: {{ home }}/calamari
        - require:
            - cmd: make-check
            - file: {{ home }}/teuthology/archive/info.yaml
