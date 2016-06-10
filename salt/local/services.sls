{% if grains['os'] == 'RedHat' and grains['osrelease'].startswith('7') %}
# Work around https://github.com/saltstack/salt/pull/12316
supervisord:
  cmd:
    - run
    - user: root
    - name: systemctl enable supervisord && systemctl start supervisord
{% else %}
supervisord:
  service:
    - running
    - enable: True
{% endif %}
