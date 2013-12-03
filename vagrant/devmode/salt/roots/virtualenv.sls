
virtualenv:
  virtualenv.managed:
    - user: vagrant
    - name: /home/vagrant/calamari/env
    - system_site_packages: true
    - require:
      - git: git_clone
      - pkg: build_deps

pip_pkgs:
  pip:
    - installed
    - user: vagrant
    - bin_env: /home/vagrant/calamari/env
    - activate: true
    - requirements: /home/vagrant/calamari/requirements.txt
    - download_cache: /vagrant/pip_cache
    - require:
      - virtualenv: virtualenv

carbon:
  pip:
    - installed
    - user: vagrant
    - bin_env: /home/vagrant/calamari/env
    - activate: true
    - install_options:
      - "--prefix=/home/vagrant/calamari/env"
      - "--install-lib=/home/vagrant/calamari/env/lib/python2.7/site-packages"
  require:
    # Carbon inserts its packages into twisted's folders so it only works
    # if installed after twisted (graphite packaging is wonky generally)
    pip: pip_pkgs

graphite-web:
  pip:
    - installed
    - user: vagrant
    - bin_env: /home/vagrant/calamari/env
    - activate: true
    - install_options:
      - "--prefix=/home/vagrant/calamari/env"
      - "--install-lib=/home/vagrant/calamari/env/lib/python2.7/site-packages"
