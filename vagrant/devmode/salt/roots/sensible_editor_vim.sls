install_vim:
  pkg.installed:
    - pkgs:
      - vim


get_vimconf:
  git:
    - latest
    - user: vagrant
    - target: /home/vagrant/dotfiles
    - name: https://github.com/gregmeno/dotfiles.git

setup_vimconf:
  cmd.run:
    - name: ./runme.sh
    - cwd: /home/vagrant/dotfiles
    - require:
        - git: get_vimconf
