{% import 'setvars' as vars %}

build-calamari-server:
  cmd.run:
    - user: {{vars.username}}
    - name: make dpkg
    - cwd: {{vars.builddir}}/calamari
{% if vars.username == 'vagrant' -%}
    - require:
      - git: {{vars.gitpath}}/calamari
{%- else -%}
    - require:
      - file: {{vars.builddir}}/calamari
{%- endif -%}

{% if vars.username != 'vagrant' %}
ensure-pkgdest-present:
  file.directory:
    - user: {{vars.username}}
    - name: {{vars.pkgdest}}
{% endif %}

{% for path in ('calamari-server_*.deb',) %}

cp-artifacts-to-share {{ path }}:
  cmd.run:
    - name: cp {{ path }} {{vars.pkgdest}}
    - cwd: {{vars.builddir}}

{% endfor %}
