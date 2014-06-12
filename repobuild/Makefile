
ubuntu:
	reprepro --confdir=./conf/ubuntu --noskipold -b ./ubuntu/ update
	# Using plain salt-minion for the moment (#6855)
	#       reprepro -b ubuntu/ includedeb precise ../../calamari-salt-minion_*.deb
	reprepro --confdir=./conf/ubuntu -b ./ubuntu/ remove precise diamond
	reprepro --confdir=./conf/ubuntu --noskipold -b ./ubuntu/ includedeb precise ../../Diamond/build/*.deb
	tar czf calamari-repo-ubuntu.tar.gz ubuntu/

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

clean:
	rm -rf el6 rhel6 ubuntu wheezy

.PHONY: ubuntu wheezy el6 rhel6 clean
