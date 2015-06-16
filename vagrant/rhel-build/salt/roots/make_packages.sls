{% import 'setvars' as vars %}

build-diamond:
  cmd.run:
    - user: {{vars.username}}
    - name: make rpm
    - cwd: {{vars.builddir}}/Diamond
    - require:
      - git: {{vars.gitpath}}/Diamond

build-repo:
  cmd.run:
    - user: {{vars.username}}
    - name: make rhel6
    - cwd: {{vars.builddir}}/calamari/repobuild
    - require:
      - git: {{vars.gitpath}}/calamari
      - cmd: build-diamond

build-calamari-server:
  cmd.run:
    - user: {{vars.username}}
    - name: ./build-rpm.sh
    - cwd: {{vars.builddir}}/calamari
    - require:
      - git: {{vars.gitpath}}/calamari

{% if vars.username != 'vagrant' %}
ensure-pkgdest-present:
  file.directory:
    - user: {{vars.username}}
    - name: {{vars.pkgdest}}
{% endif %}

{% for path in ('calamari/repobuild/calamari-repo-*.tar.gz',
                'rpmbuild/RPMS/*/calamari-server-*.rpm',
                'Diamond/dist/diamond-*.rpm') %}

cp-artifacts-to-share {{ path }}:
  cmd.run:
    - name: cp {{ path }} {{vars.pkgdest}} 
    - cwd: {{vars.builddir}}

{% endfor %}
