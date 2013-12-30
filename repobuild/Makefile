
all:
	reprepro -b . update
	reprepro -b . includedeb precise ../../calamari-salt-minion_*.deb
	reprepro -b . includedeb precise ../../Diamond/build/*.deb
	tar czf calamari-repo.tar.gz dists pool

clean:
	rm -rf db dists lists pool
   
