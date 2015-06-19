carbon.conf:
  file:
    - copy
    - user: {{ pillar['username'] }}
    - name: /home/{{ pillar['username'] }}/calamari/env/conf/carbon.conf
    - source: /home/{{ pillar['username'] }}/calamari/env/conf/carbon.conf.example
  require:
    - sls: virtualenv

storage-schemas.conf:
  file:
    - copy
    - user: {{ pillar['username'] }}
    - name: /home/{{ pillar['username'] }}/calamari/env/conf/storage-schemas.conf
    - source: /home/{{ pillar['username'] }}/calamari/env/conf/storage-schemas.conf.example
  require:
    - sls: virtualenv

storage_log_webapp:
  file:
    - directory
    - user: {{ pillar['username'] }}
    - makedirs: true
    - name: /home/{{ pillar['username'] }}/calamari/env/storage/log/webapp
  require:
    - sls: virtualenv

storage:
  file:
    - directory
    - user: {{ pillar['username'] }}
    - makedirs: true
    - name: /home/{{ pillar['username'] }}/calamari/env/storage
  require:
    - sls: virtualenv
