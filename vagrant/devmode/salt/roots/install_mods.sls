
rest_api_mod:
  cmd.run:
    - user: {{ pillar['username'] }}
    - name: "source ../env/bin/activate && python setup.py develop"
    - cwd: {{ pillar['home'] }}/calamari/rest-api
    - require:
      - sls: virtualenv

minion_sim_mod:
  cmd.run:
    - user: {{ pillar['username'] }}
    - name: "source ../env/bin/activate && python setup.py develop"
    - cwd: {{ pillar['home'] }}/calamari/minion-sim
    - require:
      - sls: virtualenv

cthulhu_mod:
  cmd.run:
    - user: {{ pillar['username'] }}
    - name: "source ../env/bin/activate && python setup.py develop"
    - cwd: {{ pillar['home'] }}/calamari/cthulhu
    - require:
      - sls: virtualenv

calamari_web_mod:
  cmd.run:
    - user: {{ pillar['username'] }}
    - name: "source ../env/bin/activate && python setup.py develop"
    - cwd: {{ pillar['home'] }}/calamari/calamari-web
    - require:
      - sls: virtualenv

calamari_common_mod:
  cmd.run:
    - user: {{ pillar['username'] }}
    - name: "source ../env/bin/activate && python setup.py develop"
    - cwd: {{ pillar['home'] }}/calamari/calamari-common
    - require:
      - sls: virtualenv
