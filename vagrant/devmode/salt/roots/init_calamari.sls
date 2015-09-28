

init_config:
  cmd.run:
    - user: {{ pillar['username'] }}
    - name: "source {{ pillar['home'] }}/calamari/env/bin/activate && dev/configure.py"
    - cwd: "{{ pillar['home'] }}/calamari"


init_rest_db:
  cmd.run:
    - user: {{ pillar['username'] }}
    - name: "source {{ pillar['home'] }}/calamari/env/bin/activate && CALAMARI_CONFIG=dev/calamari.conf calamari-ctl --devmode initialize --admin-username admin --admin-password admin --admin-email admin@admin.com"
    - cwd: "{{ pillar['home'] }}/calamari"
  require:
    - cmd: init_config
