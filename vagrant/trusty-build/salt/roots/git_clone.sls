{% import 'setvars' as vars %}

{# if not in vagrant, there's no need to reclone #}
{% if vars.username == 'vagrant' %}
calamari_clone:
  git:
    - latest
    - user: {{vars.username}}
    - target: {{vars.builddir}}/calamari
    - name: {{vars.gitpath}}/calamari
    - require:
      - pkg: build_deps

{% else %}
calamari_clone:
  file.symlink:
    - name: {{vars.builddir}}/calamari
    - target: {{vars.builddir}}
{% endif %}
