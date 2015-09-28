git_clone:
  git:
    - latest
    - user: {{ pillar['username'] }}
    - target: {{ pillar['home'] }}/calamari
    - name: /calamari.git
    - require:
      - pkg: build_deps
