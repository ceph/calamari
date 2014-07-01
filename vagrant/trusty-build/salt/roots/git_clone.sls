calamari_clone:
  git:
    - latest
    - user: vagrant
    - target: /home/vagrant/calamari
    - name: /git/calamari
    - require:
      - pkg: build_deps

diamond_clone:
  git:
    - latest
    - user: vagrant
    - target: /home/vagrant/Diamond
    - name: /git/Diamond
    - require:
      - pkg: build_deps

#salt_clone:
#  git:
#    - latest
#    - user: vagrant
#    - target: /home/vagrant/calamari-salt
#    - name: /git/calamari-salt
#    - require:
#      - pkg: build_deps
