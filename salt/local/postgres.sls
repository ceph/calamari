
{% if grains['os_family'] == 'RedHat' %}

postgresql_initdb:
    cmd:
        - run
        - name: service postgresql initdb

# change 'host' auth to 'md5' for local hashed-password authorization
/var/lib/pgsql/data/pg_hba.conf:
    file.replace:
        - pattern: ^host(.*)ident
        - repl: host\1md5
        - require:
            - cmd: postgresql_initdb

# start the service after editing pg_hba.conf
postgresql:
    service.running:
        - enable: True
    require:
        - file: /var/lib/pgsql/data/pg_hba.conf

{% else %}

# none of the above appears to be necessary with Debian
postgresql:
    service.running:
        - enable: True

{% endif %}

calamariuser:
    postgres_user.present:
        - name: calamari
        - password: 27HbZwr*g
        - user: postgres
        - require:
            - service: postgresql

calamaridb:
    postgres_database.present:
        - name: 'calamari'
        - encoding: UTF8
        - lc_ctype: en_US.UTF8
        - lc_collate: en_US.UTF8
        - template: template0
        - owner: calamari
        - user: postgres
        - require:
          - postgres_user: calamariuser
