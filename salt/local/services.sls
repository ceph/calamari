{% if grains['os_family'] == 'RedHat' and grains['osrelease'].startswith('7') %}
  {% set supervisor_service = 'supervisord.service' %}
{% else %}
  {% set supervisor_service = 'supervisor.service' %}
{% endif %}

# Work around https://github.com/saltstack/salt/pull/12316
{{supervisor_service}}:
  cmd:
    - run
    - user: root
    - name: systemctl enable {{supervisor_service}} && systemctl start {{supervisor_service}}

limit-memory:
  cmd:
    - run
    - user: root
    - name: systemctl set-property {{supervisor_service}} MemoryLimit=300M
    - require:
        - cmd: {{supervisor_service}}
