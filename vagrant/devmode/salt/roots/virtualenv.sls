
virtualenv:
  virtualenv.managed:
    - user: {{ pillar['username'] }}
    - name: {{ pillar['home'] }}/calamari/env
    - system_site_packages: true
    - require:
      - git: git_clone
      - pkg: build_deps

# Explicit installation for pyzmq so we can pass --zmq=bundled
pyzmq:
  pip.installed:
    - name: pyzmq == 14.1.1
    - user: {{ pillar['username'] }}
    - bin_env: {{ pillar['home'] }}/calamari/env
    - download_cache: {{ pillar['home'] }}/pip_cache
    - install_options:
      - "--zmq=bundled"
    - require:
      - virtualenv: virtualenv

pip_pkgs:
  pip:
    - installed
    - user: {{ pillar['username'] }}
    - bin_env: {{ pillar['home'] }}/calamari/env
    - requirements: {{ pillar['home'] }}/calamari/requirements/2.7/requirements.txt
    - download_cache: {{ pillar['home'] }}/pip_cache
    - require:
      - virtualenv: virtualenv
      - pip: pyzmq

pip_force_pkgs:
  pip:
    - installed
    - user: {{ pillar['username'] }}
    - bin_env: {{ pillar['home'] }}/calamari/env
    - requirements: {{ pillar['home'] }}/calamari/requirements/2.7/requirements.force.txt
    - ignore_installed: true
    - download_cache: {{ pillar['home'] }}/pip_cache
    - require:
      - virtualenv: virtualenv
      - pip: pyzmq

carbon:
  pip:
    - installed
    - user: {{ pillar['username'] }}
    - bin_env: {{ pillar['home'] }}/calamari/env
    - download_cache: {{ pillar['home'] }}/pip_cache
    - install_options:
      - "--prefix={{ pillar['home'] }}/calamari/env"
      - "--install-lib={{ pillar['home'] }}/calamari/env/lib/python2.7/site-packages"
    - require:
      # Carbon inserts its packages into twisted's folders so it only works
      # if installed after twisted (graphite packaging is wonky generally)
      - pip: pip_pkgs
      - pip: pip_force_pkgs

graphite-web:
  pip:
    - name: git+https://github.com/ceph/graphite-web.git@calamari
    - installed
    - user: {{ pillar['username'] }}
    - bin_env: {{ pillar['home'] }}/calamari/env
    - activate: true
    - install_options:
      - "--prefix={{ pillar['home'] }}/calamari/env"
      - "--install-lib={{ pillar['home'] }}/calamari/env/lib/python2.7/site-packages"
