build-diamond:
  cmd.run:
    - name: make deb
    - cwd: /home/vagrant/Diamond
    - require:
      - git: /git/Diamond

build-repo:
  cmd.run:
    - name: make
    - cwd: /home/vagrant/calamari/repobuild
    - require:
      - git: /git/calamari

build-calamari-server:
  cmd.run:
    - name: make dpkg
    - cwd: /home/vagrant/calamari
    - require:
      - git: /git/calamari


{% for path in ('calamari/repobuild/calamari-repo.tar.gz',
                'calamari-server_1.0.0-1_all.deb',
                'Diamond/build/diamond_3.4.58_all.deb') %}

cp-artifacts-to-share {{ path }}:
  cmd.run:
    - name: cp {{ path }} /git/
    - cwd: /home/vagrant/

{% endfor %}
