infoyaml:  |
  master_fqdn:
    vagrant-ubuntu-trusty-64:8000

  cluster:
    vagrant@vagrant-ubuntu-trusty-64:
        roles:
        - mon.1
        - osd.1
        - client.0
