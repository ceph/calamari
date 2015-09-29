carbon.conf:
  file:
    - copy
    - user: {{ pillar['username'] }}
    - name: {{ pillar['home'] }}/calamari/env/conf/carbon.conf
    - source: {{ pillar['home'] }}/calamari/env/conf/carbon.conf.example
  require:
    - sls: virtualenv

storage-schemas.conf:
  file:
    - copy
    - user: {{ pillar['username'] }}
    - name: {{ pillar['home'] }}/calamari/env/conf/storage-schemas.conf
    - source: {{ pillar['home'] }}/calamari/env/conf/storage-schemas.conf.example
  require:
    - sls: virtualenv

storage_log_webapp:
  file:
    - directory
    - user: {{ pillar['username'] }}
    - makedirs: true
    - name: {{ pillar['home'] }}/calamari/env/storage/log/webapp
  require:
    - sls: virtualenv

storage:
  file:
    - directory
    - user: {{ pillar['username'] }}
    - makedirs: true
    - name: {{ pillar['home'] }}/calamari/env/storage
  require:
    - sls: virtualenv
