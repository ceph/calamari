packages:
  pkg.installed:
    - pkgs:
      - python-virtualenv
      - python-pip

/var/cluster/env:
  virtualenv.managed:
    - system_site_packages: False
    - require:
        - pkg: packages

ceph-deploy:
  pip.installed:
    - name: ceph-deploy
    - bin_env: /var/cluster/env
    - require:
      - pkg: packages
      - virtualenv: /var/cluster/env

/var/cluster/ceph-deploy:
    file.directory:
    - user: root
    - group: root
    - dir_mode: 755
    - file_mode: 644
    - recurse:
        - user
        - group
        - mode

munge-hosts-file:
  cmd.run:
    - name: ip addr | grep eth | grep inet | sed "s/\// $(hostname -s) /;1q" | awk '{print $2 " " $3}' >> /etc/hosts # SOOOO GROSS

new-cluster:
  cmd.run:
    - name: /var/cluster/env/bin/ceph-deploy new {{ grains['fqdn'] }}
    - cwd: /var/cluster
    - require:
        - pip: ceph-deploy
        - cmd: munge-hosts-file

modify-ceph.conf:
    cmd.run:
        - name: echo '''osd pool default size = 1''' >> /var/cluster/ceph.conf
        - require:
            - cmd: new-cluster

install-cluster:
  cmd.run:
    - name: /var/cluster/env/bin/ceph-deploy install {{ grains['fqdn'] }}
    - cwd: /var/cluster
    - require:
        - cmd: modify-ceph.conf

mon-create:
  cmd.run:
    - name: /var/cluster/env/bin/ceph-deploy mon create-initial
    - cwd: /var/cluster
    - require:
        - cmd: install-cluster

/var/cluster/osd:
    file.directory:
    - user: ceph
    - group: ceph
    - dir_mode: 755
    - file_mode: 644
    - recurse:
        - user
        - group
        - mode

osd-prepare:
  cmd.run:
    - name: /var/cluster/env/bin/ceph-deploy osd prepare {{ grains['fqdn'] }}:/var/cluster/osd
    - cwd: /var/cluster
    - require:
        - cmd: mon-create
        - file: /var/cluster/osd

osd-activate:
  cmd.run:
    - name: /var/cluster/env/bin/ceph-deploy osd activate {{ grains['fqdn'] }}:/var/cluster/osd
    - cwd: /var/cluster
    - require:
        - cmd: osd-prepare
