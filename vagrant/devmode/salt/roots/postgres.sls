{% if grains['os_family'] == 'RedHat' %}

{% if grains['osrelease'] == '21' or grains['osmajorrelease'] == '7' %}
# work around https://github.com/saltstack/salt/pull/12316; use new
# command postgresql-setup anyway

postgresql_status:
    cmd:
        - run
        - user: postgres
        - name: pg_ctl status -D /var/lib/pgsql/data

postgresql_initdb:
    cmd:
        - run
        - name: postgresql-setup initdb
        - onfail:
           - cmd: postgresql_status

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
        - name: systemctl enable postgresql.service || true; systemctl stop postgresql.service || true; systemctl start postgresql.service || true
        - require:
            - cmd: postgresql_status

calamariuser:
    postgres_user.present:
        - name: calamari
        - password: 27HbZwr*g
        - createdb: true
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

{% endif %}
{% else %}

postgresql:
    service.running:
        - enable: True

calamariuser:
    postgres_user.present:
        - name: calamari
        - password: 27HbZwr*g
        - createdb: true
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


