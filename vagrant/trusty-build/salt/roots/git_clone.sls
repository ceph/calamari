{% import 'setvars' as vars %}

calamari_clone:
  git:
    - latest
    - user: {{vars.username}}
    - target: {{vars.builddir}}/calamari
    - name: {{vars.gitpath}}/calamari
    - force_reset: True
    - require:
      - pkg: build_deps

diamond_clone:
  git:
    - latest
    - user: {{vars.username}}
    - target: {{vars.builddir}}/Diamond
    - name: {{vars.gitpath}}/Diamond
    - force_reset: True
    - require:
      - pkg: build_deps
