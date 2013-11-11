
# Network configuration for john.spray@inktank.com's development cluster
# the 'network' states only work on RHEL :-(

#

{% if grains['os_family'] == 'RedHat' %}
p1p1:
  network.managed:
    - type: eth
    - enabled: True
    - ipaddr: 192.168.18.{{ grains['host']|replace("gravel", "") }}
    - netmask: 255.255.255.0
p1p2:
  network.managed:
    - type: eth
    - enabled: True
    - ipaddr: 192.168.19.{{ grains['host']|replace("gravel", "") }}
    - netmask: 255.255.255.0
{% elif grains['os_family'] == 'Debian' %}
/etc/network/interfaces:
  file.managed:
    - source: salt://rockery/interfaces
    - template: jinja

start-p1p1:
  cmd.run:
    - name: "ifup p1p1"
    - unless: "ifconfig | grep p1p1"

start-p1p2:
  cmd.run:
    - name: "ifup p1p2"
    - unless: "ifconfig | grep p1p2"

{% endif %}

