{% import 'setvars' as vars %}

calamari_clone:
  git:
    - latest
    - user: {{vars.username}}
    - target: {{vars.builddir}}/calamari
    - name: {{vars.gitpath}}/calamari
    - require:
      - pkg: build_deps
