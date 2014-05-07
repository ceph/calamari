build-diamond:
  cmd.run:
    - user: vagrant
    - name: make rpm
    - cwd: /home/vagrant/Diamond
    - require:
      - git: /git/Diamond

build-repo:
  cmd.run:
    - user: vagrant
    - name: make rhel6
    - cwd: /home/vagrant/calamari/repobuild
    - require:
      - git: /git/calamari
      - cmd: build-diamond

build-calamari-server:
  cmd.run:
    - user: vagrant
    - name: ./build-rpm.sh
    - cwd: /home/vagrant/calamari
    - require:
      - git: /git/calamari

{% for path in ('calamari/repobuild/calamari-repo-rhel6.tar.gz',
                'rpmbuild/RPMS/x86_64/calamari-server-*.rpm',
                'Diamond/dist/diamond-*.noarch.rpm') %}

cp-artifacts-to-share {{ path }}:
  cmd.run:
    - name: cp {{ path }} /git/
    - cwd: /home/vagrant/

{% endfor %}
