
ubuntu:
	mkdir ubuntu || true
	reprepro --noskipold -b ubuntu/ update
	# Using plain salt-minion for the moment (#6855)
	#       reprepro -b ubuntu/ includedeb precise ../../calamari-salt-minion_*.deb
	reprepro -b ubuntu/ remove precise diamond
	reprepro --noskipold -b ubuntu/ includedeb precise ../../Diamond/build/*.deb
	tar czf calamari-repo-ubuntu.tar.gz ubuntu/

el6:
	mkdir el6 || true
	yumdownloader --destdir=el6 salt-minion m2crypto openpgm python-babel python-jinja2 python-msgpack python-yaml python-zmq salt sshpass zeromq3
	cp ../../Diamond/dist/*.noarch.rpm el6/
	createrepo el6
	tar czf calamari-repo-el6.tar.gz el6/

clean:
	rm -rf el6 ubuntu
