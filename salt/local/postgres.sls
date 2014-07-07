
{% if grains['os_family'] == 'RedHat' %}

{% if grains['osrelease'] == '7.0' %}
# work around https://github.com/saltstack/salt/pull/12316; use new
# command postgresql-setup anyway
postgresql_initdb:
    cmd:
        - run
        - name: postgresql-setup initdb

# change 'host' auth to 'md5' for local hashed-password authorization
/var/lib/pgsql/data/pg_hba.conf:
    file.replace:
        - pattern: host(.*)ident
        - repl: host\1md5
        - require:
            - cmd: postgresql_initdb

# start the service after editing pg_hba.conf
postgresql:
    cmd:
        - run
        - name: systemctl enable postgresql || true; systemctl stop postgresql || true; systemctl start postgresql || true
        - require:
            - file: /var/lib/pgsql/data/pg_hba.conf

calamariuser:
    postgres_user.present:
        - name: calamari
        - password: 27HbZwr*g
        - user: postgres
        - require:
            - cmd: postgresql

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

{% else %}

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

postgresql:
    service.running:
        - enable: True
    require:
        - file: /var/lib/pgsql/data/pg_hba.conf

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

{% endif %}

{% else %}

# none of the above appears to be necessary with Debian
postgresql:
    service.running:
        - enable: True

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

{% endif %}
