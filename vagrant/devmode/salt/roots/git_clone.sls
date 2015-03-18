git_clone:
  git:
    - latest
    - user: {{ pillar[username] }}
    - target: /home/{{ pillar[username] }}/calamari
    - name: /home/{{ pillar[username] }}/the_source
    - require:
      - pkg: build_deps
