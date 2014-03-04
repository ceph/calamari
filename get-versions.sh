#!/bin/bash
#
# Output version, revision for package builds derived from git.
#
# -r: change revision to be suitable for rpm
# VERSION: output X only
# REVISION: output Y only
# no more args: output VERSION=X REVISION=Y suitable for eval
#

RPM='n'
if [ "$1" == "-r" ] ; then RPM='y' ; shift ; fi

# GITVER is the version from the current git branch, less the first char ('v')
GITVER=$(git describe | cut -c 2-)

# if GITVER contains a '-', separate at the first one into version and revision
if [[ $GITVER == *-* ]]; then
	VERSION=$(echo $GITVER | sed 's/-.*//')
	REVISION=$(echo $GITVER | sed 's/'${VERSION}'-//')
	if [ $RPM == 'y' ] ; then
		REVISION=$(echo $REVISION | sed 's/-/_/g')
	fi
else
	VERSION=$GITVER
	REVISION="0"
fi

case "$1" in
	VERSION) echo $VERSION; exit ;;
	REVISION) echo $REVISION; exit ;;
	*) echo "VERSION=$VERSION REVISION=$REVISION"; exit ;;
esac
