
rest_api_mod:
  cmd.run:
    - user: vagrant
    - name: "source ../env/bin/activate && python setup.py develop"
    - cwd: /home/vagrant/calamari/rest-api
    - require:
      - sls: virtualenv

minion_sim_mod:
  cmd.run:
    - user: vagrant
    - name: "source ../env/bin/activate && python setup.py develop"
    - cwd: /home/vagrant/calamari/minion-sim
    - require:
      - sls: virtualenv

cthulhu_mod:
  cmd.run:
    - user: vagrant
    - name: "source ../env/bin/activate && python setup.py develop"
    - cwd: /home/vagrant/calamari/cthulhu
    - require:
      - sls: virtualenv

calamari_web_mod:
  cmd.run:
    - user: vagrant
    - name: "source ../env/bin/activate && python setup.py develop"
    - cwd: /home/vagrant/calamari/calamari-web
    - require:
      - sls: virtualenv

calamari_common_mod:
  cmd.run:
    - user: vagrant
    - name: "source ../env/bin/activate && python setup.py develop"
    - cwd: /home/vagrant/calamari/calamari-common
    - require:
      - sls: virtualenv

