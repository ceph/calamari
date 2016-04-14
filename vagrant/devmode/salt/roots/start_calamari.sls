supervisord:
    cmd.run:
        - user: root
        - name: source env/bin/activate; supervisord -c dev/supervisord.conf
        - cwd: {{ pillar['home'] }}/calamari
        - unless: pgrep supervisord
