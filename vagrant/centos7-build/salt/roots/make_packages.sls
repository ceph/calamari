{% import 'setvars' as vars %}

build-calamari-server:
  cmd.run:
    - user: {{vars.username}}
    - name: ./build-rpm.sh
    - cwd: {{vars.builddir}}/calamari
    - require:
      - git: {{vars.gitpath}}/calamari

{% for path in ('calamari/repobuild/calamari-repo-*.tar.gz',
                'rpmbuild/RPMS/*/calamari-server-*.rpm',
                'Diamond/dist/diamond-*.rpm') %}

cp-artifacts-up {{ path }}:
  cmd.run:
    - name: cp {{ path }} {{vars.pkgdest}}
    - cwd: {{vars.builddir}}

{% endfor %}
