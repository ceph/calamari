
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
    - requirements: {{ pillar['home'] }}/calamari/requirements/lite.txt
    - ignore_installed: true
    - download_cache: {{ pillar['home'] }}/pip_cache
    - require:
      - virtualenv: virtualenv
      - pip: pyzmq
