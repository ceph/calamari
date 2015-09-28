git_clone:
  git:
    - latest
    - user: vagrant
    - target: /home/vagrant/calamari
    - name: /calamari.git
    - require:
      - pkg: build_deps
