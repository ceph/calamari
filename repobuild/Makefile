precise:
	reprepro --confdir=./conf/precise --noskipold -b ./precise/ update
	# Using plain salt-minion for the moment (#6855)
	#       reprepro -b ubuntu/ includedeb precise ../../calamari-salt-minion_*.deb
	reprepro --confdir=./conf/precise -b ./precise/ remove precise diamond
	reprepro --confdir=./conf/precise --noskipold -b ./precise/ includedeb precise ../../Diamond/build/*.deb
	tar czf calamari-repo-precise.tar.gz precise/

trusty:
	reprepro --confdir=./conf/trusty --noskipold -b ./trusty/ update
	# Using plain salt-minion for the moment (#6855)
	#       reprepro -b ubuntu/ includedeb precise ../../calamari-salt-minion_*.deb
	reprepro --confdir=./conf/trusty -b ./trusty/ remove trusty diamond
	reprepro --confdir=./conf/trusty --noskipold -b ./ubuntu/ includedeb trusty ../../Diamond/build/*.deb
	tar czf calamari-repo-trusty.tar.gz trusty/

wheezy:
	reprepro --confdir=./conf/wheezy --noskipold -b ./wheezy/ update
	# Using plain salt-minion for the moment (#6855)
	#       reprepro -b ubuntu/ includedeb precise ../../calamari-salt-minion_*.deb
	reprepro --confdir=./conf/wheezy -b ./wheezy/ remove wheezy diamond
	reprepro --confdir=./conf/wheezy --noskipold -b ./wheezy/ includedeb wheezy ../../Diamond/build/*.deb
	tar czf calamari-repo-wheezy.tar.gz wheezy/

el6:
	mkdir el6 || true
	yumdownloader --destdir=el6 --archlist=x86_64 -x '*i686*' salt-minion m2crypto openpgm python-babel python-jinja2 python-msgpack PyYAML python-zmq salt sshpass zeromq3 python-crypto libyaml
	cp ../../Diamond/dist/*.noarch.rpm el6/
	createrepo el6
	tar czf calamari-repo-el6.tar.gz el6/

rhel6:
	mkdir rhel6 || true
	sudo yumdownloader --destdir=rhel6 --archlist=x86_64 -x '*i686*' salt-minion m2crypto openpgm python-babel python-jinja2 python-msgpack PyYAML python-zmq salt sshpass zeromq3 python-crypto libyaml
	cp ../../Diamond/dist/*.noarch.rpm rhel6/
	createrepo rhel6
	tar czf calamari-repo-rhel6.tar.gz rhel6/

# before it got to EPEL7, we did this; supposed to be there now
#RHEL7_SALT_LOC=http://apt-mirror.sepia.ceph.com/misc-rpms/
#SALT_RPMS=salt-2014.1.4-1_ceph.el7.noarch.rpm salt-minion-2014.1.4-1_ceph.el7.noarch.rpm

rhel7:
	mkdir rhel7 || true
	yumdownloader --destdir=rhel7 m2crypto openpgm python-babel python-jinja2 python-msgpack PyYAML python-zmq sshpass zeromq3 python-crypto libyaml salt salt-minion
	# for r in $(SALT_RPMS); do curl -sS $(RHEL7_SALT_LOC)/$$r -o rhel7/$$r; done
	cp ../../Diamond/dist/*.noarch.rpm rhel7/
	createrepo rhel7
	tar czf calamari-repo-rhel7.tar.gz rhel7/

clean:
	rm -rf el6 rhel6 rhel7 ubuntu wheezy

.PHONY: precise trusty wheezy el6 rhel6 rhel7 clean
