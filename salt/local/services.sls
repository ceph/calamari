{% if grains['os_family'] == 'RedHat' %}
  {% set apache_service = 'httpd' %}
{% else %}
  {% set apache_service = 'apache' %}
{% endif %}

{% if grains['os'] == 'RedHat' and grains['osrelease'].startswith('7') %}
# Work around https://github.com/saltstack/salt/pull/12316
{{ apache_service }}:
  cmd:
    - run
    - user: root
    - name: systemctl enable {{ apache_service }} && systemctl start {{ apache_service }}

supervisord:
  cmd:
    - run
    - user: root
    - name: systemctl enable supervisord && systemctl start supervisord

salt-master:
  cmd:
    - run
    - user: root
    - name: systemctl enable salt-master && systemctl start salt-master

{% else %}

{{ apache_service }}:
  service:
    - running
    - enable: True

supervisord:
  service:
    - running
    - enable: True

salt-master:
  service:
    - running
    - enable: True

{% endif %}
