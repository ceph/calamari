# adapted from 1.1's jenkins build script, aiming for self-reliance
cd ..
WORKSPACE=$(pwd)

RPMBUILD=${WORKSPACE}/rpmbuild
DISTDIR=${WORKSPACE}/dist
rm -rf ${RPMBUILD} ${DISTDIR}

# Build tarball
(cd ${WORKSPACE}/calamari; make dist)
TARNAME="calamari-server_*tar.gz"

# Set up build area
mkdir -p ${RPMBUILD}/{SOURCES,SRPMS,SPECS,RPMS,BUILD}
cp -a ${TARNAME} ${RPMBUILD}/SOURCES
cp -a calamari/calamari.spec ${RPMBUILD}/SPECS

# set VERSION and REVISION
eval $(cd ${WORKSPACE}/calamari; ./get-versions.sh -r)

# Build RPMs
cd ${RPMBUILD}
rpmbuild -ba --define "_topdir ${RPMBUILD}" --define "_unpackaged_files_terminate_build 0" --define "version ${VERSION}" --define "revision ${REVISION}" SPECS/calamari.spec

# Copy to dist directory
cd ${WORKSPACE}
REPO=${DISTDIR}/${DIST}
mkdir -p ${REPO}
cp -a ${RPMBUILD}/SRPMS ${REPO}
cp -a ${RPMBUILD}/RPMS/* ${REPO}

# XXX who signs when?

## Sign the rpms
#for RPMPKG in `find ${REPO} -name "*.rpm"`
#do
#    ${CEPH_BUILD_DIR}/rpm-autosign.exp --define "_gpg_name ${KEYID}" ${RPMPKG}
#done

# Index and sign the repo.
createrepo ${REPO}
#gpg --batch --yes --detach-sign --armor -u ${KEYID} ${REPO}/repodata/repomd.xml
#
#echo "done"
#exit 0
