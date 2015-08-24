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

config-tests-converged:
    cmd.run:
        - name: sed 's/embedded/external/;s/ceph_control = external/ceph_control = converged/' -i /home/vagrant/calamari/tests/test.conf

config-tests-no-bootstrap:
    cmd.run:
        - name: echo 'bootstrap = False' >> /home/vagrant/calamari/tests/tests.conf

/home/vagrant/teuthology/archive:
    file.directory:
    - user: vagrant
    - group: vagrant
    - dir_mode: 755
    - file_mode: 644
    - recurse:
        - user
        - group
        - mode

/home/vagrant/teuthology/archive/info.yaml:
    file.managed:
        - user: vagrant
        - group: vagrant
        - file_mode: 644
        - contents_pillar: infoyaml
        - contents_newline: False
        - require:
            - file: /home/vagrant/teuthology/archive

make-check:
    cmd.run:
        - name: source env/bin/activate; make check
        - cwd: /home/vagrant/calamari
        - require:
            - cmd: supervisord

supervisord:
    cmd.run:
        - name: source env/bin/activate; supervisord -c dev/supervisord.conf
        - cwd: /home/vagrant/calamari

nosetests:
    cmd.run:
        - name: source env/bin/activate; nosetests tests
        - cwd: /home/vagrant/calamari
        - require:
            - cmd: make-check
            - cmd: config-tests-converged
            - cmd: config-tests-no-bootstrap
            - file: /home/vagrant/teuthology/archive/info.yaml
