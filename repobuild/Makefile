
all:
	reprepro --noskipold -b . update
	# Using plain salt-minion for the moment
	#	reprepro -b . includedeb precise ../../calamari-salt-minion_*.deb
	reprepro -b . remove precise diamond
	reprepro --noskipold -b . includedeb precise ../../Diamond/build/*.deb
	tar czf calamari-repo.tar.gz dists pool

clean:
	rm -rf db dists lists pool
   
