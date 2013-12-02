
init_rest_db:
  cmd.run:
    - name: "/home/vagrant/calamari/env/bin/python calamari-ctl initialize"
    - cwd: "/home/vagrant/calamari"
