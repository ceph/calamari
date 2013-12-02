carbon.conf:
  file:
    - copy
    - user: vagrant
    - name: /home/vagrant/calamari/env/conf/carbon.conf
    - source: /home/vagrant/calamari/env/conf/carbon.conf.example
  require:
    - sls: virtualenv

storage-schemas.conf:
  file:
    - copy
    - user: vagrant
    - name: /home/vagrant/calamari/env/conf/storage-schemas.conf
    - source: /home/vagrant/calamari/env/conf/storage-schemas.conf.example
  require:
    - sls: virtualenv

storage_log_webapp:
  file:
    - directory
    - user: vagrant
    - makedirs: true
    - name: /home/vagrant/calamari/env/storage/log/webapp
  require:
    - sls: virtualenv

storage:
  file:
    - directory
    - user: vagrant
    - makedirs: true
    - name: /home/vagrant/calamari/env/storage
  require:
    - sls: virtualenv