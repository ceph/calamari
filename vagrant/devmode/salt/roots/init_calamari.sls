
init_rest_db:
  cmd.run:
    - user: vagrant
    - name: "source /home/vagrant/calamari/env/bin/activate && calamari-ctl initialize --admin-username admin --admin-password admin --admin-email admin@admin.com"
    - cwd: "/home/vagrant/calamari"
