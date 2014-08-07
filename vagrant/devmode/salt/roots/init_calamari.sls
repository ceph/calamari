

init_config:
  cmd.run:
    - user: vagrant
    - name: "source /home/vagrant/calamari/env/bin/activate && dev/configure.py"
    - cwd: "/home/vagrant/calamari"


init_rest_db:
  cmd.run:
    - user: vagrant
    - name: "source /home/vagrant/calamari/env/bin/activate && CALAMARI_CONFIG=dev/calamari.conf calamari-ctl --devmode initialize --admin-username admin --admin-password admin --admin-email admin@admin.com"
    - cwd: "/home/vagrant/calamari"
  require:
    - cmd: init_config
