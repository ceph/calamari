
{% if grains['os_family'] == 'RedHat' %}

{% if grains['osrelease'].startswith('7') or grains['osfullname'] == 'Fedora' %}
# work around https://github.com/saltstack/salt/pull/12316; use new
# command postgresql-setup anyway
{% if grains['osrelease'].startswith('7') %}
postgresql_initdb:
    cmd:
        - run
        - name: postgresql-setup initdb
{% else %}
postgresql_initdb:
    cmd:
        - run
        - name: postgresql-setup --initdb
{% endif %}

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

{% elif grains['os_family'] == 'Suse' %}

# Salt won't find the postgresql service unless systemd knows
# it exists, which it won't unless the init script has been
# invoked at least once before.  This is horrible.

rcpostgresql status >/dev/null 2>&1:
    cmd.run

# Suse needs the host auth to be md5, but doesn't have
# `service postgresql initdb`, so have to start the service
# then tweak pg_hba.conf, then HUP the service

postgresql:
    service.running:
        - enable: True

/var/lib/pgsql/data/pg_hba.conf:
    file.replace:
        - pattern: ^host(.*)ident
        - repl: host\1md5
        - require:
            - service: postgresql

reload_postgresql:
    module:
        - wait
        - name: service.reload
        - m_name: postgresql
        - watch:
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
