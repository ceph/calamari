{% import 'setvars' as vars %}

build-diamond:
  cmd.run:
    - user: {{vars.username}}
    - name: make deb
    - cwd: {{vars.builddir}}/Diamond
    - require:
      - git: {{vars.gitpath}}/Diamond

build-repo:
  cmd.run:
    - user: {{vars.username}}
    - name: make xenial
    - cwd: {{vars.builddir}}/calamari/repobuild
    - require:
      - git: {{vars.gitpath}}/calamari
      - cmd: build-diamond

build-calamari-server:
  cmd.run:
    - user: {{vars.username}}
    - name: make dpkg
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
                'calamari-server_*.deb',
                'Diamond/build/diamond_*.deb') %}

cp-artifacts-to-share {{ path }}:
  cmd.run:
    - name: cp {{ path }} {{vars.pkgdest}}
    - cwd: {{vars.builddir}}

{% endfor %}
