
virtualenv:
  virtualenv.managed:
    - user: {{ pillar['username'] }}
    - name: {{ pillar['home'] }}/calamari/env
    - system_site_packages: true
    - require:
      - git: git_clone
      - pkg: build_deps

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

devel_pip_pkgs:
  pip:
    - installed
    - user: {{ pillar['username'] }}
    - bin_env: {{ pillar['home'] }}/calamari/env
    - requirements: {{ pillar['home'] }}/calamari/requirements/devel.txt
    - download_cache: {{ pillar['home'] }}/pip_cache
    - require:
      - virtualenv: virtualenv
      - pip: pyzmq
