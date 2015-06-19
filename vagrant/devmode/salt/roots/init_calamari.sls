

init_config:
  cmd.run:
    - user: {{ pillar['username'] }}
    - name: "source /home/{{ pillar['username'] }}/calamari/env/bin/activate && dev/configure.py"
    - cwd: "/home/{{ pillar['username'] }}/calamari"


init_rest_db:
  cmd.run:
    - user: {{ pillar['username'] }}
    - name: "source /home/{{ pillar['username'] }}/calamari/env/bin/activate && CALAMARI_CONFIG=dev/calamari.conf calamari-ctl --devmode initialize --admin-username admin --admin-password admin --admin-email admin@admin.com"
    - cwd: "/home/{{ pillar['username'] }}/calamari"
  require:
    - cmd: init_config
