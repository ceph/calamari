distribute-osd-crush-location-script:
  file:
    - managed
    - name: /usr/bin/calamari-crush-location
    - source: salt://base/calamari-crush-location.py
    - mode: 755

change-ceph-conf-to-use-our-location-script:
    cmd:
        - run
        - name: find /etc/ceph -name '*.conf' |
                while read conf; 
                do 
                    echo;
                    cp "$conf" "$conf.orig";
                    echo "modifying $conf";
                    grep -EH 'osd crush update on start = false|osd crush location hook' "$conf" ||
                    sed 's/\[global\]/\[global\]\nosd crush location hook = \/usr\/bin\/calamari-crush-location/' -i "$conf"; 
                done
        - require:
            - file: distribute-osd-crush-location-script

