build-diamond:
  cmd.run:
    - user: vagrant
    - name: make deb
    - cwd: /home/vagrant/Diamond
    - require:
      - git: /git/Diamond

build-repo:
  cmd.run:
    - user: vagrant
    - name: make trusty
    - cwd: /home/vagrant/calamari/repobuild
    - require:
      - git: /git/calamari
      - cmd: build-diamond

build-calamari-server:
  cmd.run:
    - user: vagrant
    - name: make dpkg
    - cwd: /home/vagrant/calamari
    - require:
      - git: /git/calamari

{% for path in ('calamari/repobuild/calamari-repo-trusty.tar.gz',
                'calamari-server_*.deb',
                'Diamond/build/diamond_*.deb') %}

cp-artifacts-to-share {{ path }}:
  cmd.run:
    - name: cp {{ path }} /git/
    - cwd: /home/vagrant/

{% endfor %}
