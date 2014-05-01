git_clone:
  git:
    - latest
    - user: vagrant
    - target: /home/vagrant/calamari
    - name: /calamari.git
    - require:
      - pkg: build_deps

git_clone_teuthology:
  git:
    - latest
    - rev: 5339c1f2ee
    - user: vagrant
    - target: /home/vagrant/teuthology
    - name: https://github.com/ceph/teuthology.git
    - require:
      - pkg: build_deps
