postgresql:
    service.running:
        - enable: True

calamariuser:
    postgres_user.present:
        - name: calamari
        - password: 27HbZwr*g
        - runas: postgres
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
        - runas: postgres
        - require:
          - postgres_user: calamariuser
