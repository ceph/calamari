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
    - name: make el6
    - cwd: /home/vagrant/calamari/repobuild
    - require:
      - git: /git/calamari
      - cmd: build-diamond

{% for path in ('calamari/repobuild/calamari-repo-el6.tar.gz',
                'Diamond/dist/diamond-*.noarch.rpm') %}

cp-artifacts-to-share {{ path }}:
  cmd.run:
    - name: cp {{ path }} /git/
    - cwd: /home/vagrant/

{% endfor %}
