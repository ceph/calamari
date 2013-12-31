ifndef VERSION
    VERSION=$(shell ./get-versions.sh VERSION)
endif
ifndef REVISION
    REVISION=$(shell ./get-versions.sh REVISION)
endif
ifndef DIST
    DIST=unstable
endif
ifndef BPTAG
    BPTAG=""
endif
ifndef DEBEMAIL
    DEBEMAIL=dan.mick@inktank.com
endif

# debian upstream tarballs: {name}_{version}.orig.tar.gz
# rpm tarball names: apparently whatever you name in Source0, but
# {name}_{version}.tar.gz will work
DISTNAMEVER=calamari_$(VERSION)
TARNAME = ../$(DISTNAMEVER).tar.gz

# tmp dir for building the tarball
PKGDIR=calamari-$(VERSION)

SRC := $(shell pwd)

INSTALL=/usr/bin/install

UI_BASEDIR = $(DESTDIR)/opt/calamari/webapp/content
UI_SUBDIRS = ui/admin ui/login clients/dashboard

CONFIG_JSON = clients/dashboard/dist/scripts/config.json

CONFFILES = \
	conf/diamond/CephCollector.conf \
	conf/diamond/NetworkCollector.conf \
	conf/carbon/storage-schema.conf \
	conf/restapi/cephrestapi.conf \
	conf/restapi/cephrestwsgi.py \
	conf/calamari.wsgi

# Strategy for building dist tarball: find what we know is source
# "grunt clean" doesn't take us back to a pristine source dir, so instead
# we filter out what we know is build product and tar up only what we
# want in sources.

# this is crazy convoluted to work around files with spaces in their names.
# also, debian is pruned because we want to add only specific parts of it
FINDCMD =find . \
        -name .git -prune \
        -o -name node_modules -prune \
        -o -name .tmp -prune \
        -o -name .sass-cache -prune \
        -o -name debian -prune \
        -o -print0

DATESTR=$(shell /bin/echo -n "built on "; date)
set_deb_version:
	DEBEMAIL=$(DEBEMAIL) dch \
		--newversion $(VERSION)-$(REVISION)$(BPTAG) \
		-D $(DIST) --force-bad-version --force-distribution "$(DATESTR)"

build: build-ui build-venvs $(CONFIG_JSON) $(CONFFILES)

build-venvs: build-graphite-venv build-calamari-venv

build-ui:
	@echo "building ui subdirs"
	for d in $(UI_SUBDIRS); do \
		echo $$d; \
		(cd $$d; \
		npm install --silent; \
		bower --allow-root install; \
		grunt --no-color saveRevision; \
		grunt --no-color build; ) \
	done

# graphite-web's requirements are obtained from a static copy of its
# requirements.txt from github, because obviously expressing those in setup.py
# or even including them in the stuff installed with setup.py would be just
# stupid.  Of course this depends on requirements.txt actually matching
# graphite-web's pip install. arrrrrrgh.
# XXX maybe at least add some kind of versioning check?...like what?...

# *EVEN BETTER*:
# carbon install, when it senses 'redhat' in platform.dist()[0], tries
# to install scripts to /etc/init.d.  THANKS.  Download, hack the setup.py,
# and install in three steps rather than one to accommodate this braindeath.
#
# XXX we call 'bin/python bin/pip' rather than pip directly because the
# #! line in bin/pip can easily be too long; Linux can only handle 128 chars

build-graphite-venv:
	@echo "build-graphite-venv"
	(export PYTHONDONTWRITEBYTECODE=1; \
	virtualenv graphite; \
	cd graphite; \
	./bin/python ./bin/pip install whisper; \
	./bin/python ./bin/pip install --no-install carbon; \
	sed -i 's/== .redhat./== "DONTDOTHISredhat"/' \
		build/carbon/setup.py; \
	./bin/python ./bin/pip install \
          --install-option="--prefix=$(SRC)/graphite" \
	  --install-option="--install-lib=$(SRC)/graphite/lib" \
	  --no-download carbon; \
	./bin/python ./bin/pip install \
	  --install-option="--prefix=$(SRC)/graphite" \
	  --install-option="--install-lib=$(SRC)/graphite/webapp" \
	  graphite-web; \
	./bin/python ./bin/pip install -r \
	  $(SRC)/graphite-requirements.txt; \
	(find . -type f | xargs grep -l '#!.*'$(SRC) ; \
	   echo bin/activate bin/activate.csh bin/activate.fish ) | \
	while read f; do \
		echo -n "modifying $$f: "; \
		grep $(SRC) $$f; \
		sed -i -e 's;'$(SRC)';/opt;' $$f; \
	done; \
	if [ -h local/bin ] ; then \
		for p in bin include lib; do \
			rm local/$$p; \
			ln -s /opt/graphite/$$p local/$$p; \
		done; \
	fi)

build-calamari-venv:
	@echo "build-calamari-venv"
	(export PYTHONDONTWRITEBYTECODE=1; \
	mkdir calamari; \
	virtualenv calamari/venv; \
	cd calamari/venv; \
	./bin/python ./bin/pip install -r $(SRC)/requirements.txt; \
	(find . -type f | xargs grep -l '#!.*'$(SRC) ; \
	  echo bin/activate bin/activate.csh bin/activate.fish) | \
	while read f; do \
		echo -n "modifying $$f: "; \
		grep $(SRC) $$f; \
		sed -i -e 's;'$(SRC)';/opt;' $$f; \
	done; \
	if [ -h local/bin ] ; then \
		for p in bin include lib; do \
			rm local/$$p; \
			ln -s /opt/calamari/venv/$$p local/$$p; \
		done; \
	fi)

# for right now, this contains two useful things that should be set
# when running against a live cluster.  We could preinstall it in the
# package or do it in a postinstall; it has more visibility here

$(CONFIG_JSON):
	echo '{ "offline": false, "graphite-host": "/graphite" }' \
		> $(CONFIG_JSON)


# this source is just not very amenable to building source packages.
# the Javascript directories don't really go back to "clean"; it might
# be possible to change that, but for now, just skip the source build
dpkg:
	dpkg-buildpackage -b -us -uc

install-common: build install-conf install-init.d install-ui install-graphite-venv install-calamari-venv
	@echo "install-common"

install-rpm: install-common install-rh-conf
	@echo "install-rpm"

# for deb
install: install-common install-deb-conf
	@echo "install"

install-conf: $(CONFFILES)
	@echo "install-conf"
	# Diamond conf files$
	@$(INSTALL) -D conf/diamond/CephCollector.conf \
		$(DESTDIR)/etc/diamond/collectors/CephCollector.conf
	@$(INSTALL) -D conf/diamond/NetworkCollector.conf \
		$(DESTDIR)/etc/diamond/collectors/NetworkCollector.conf
	# carbon storage conf
	@$(INSTALL) -D conf/carbon/storage-schemas.conf \
		$(DESTDIR)/opt/graphite/conf/storage-schemas.conf
	# nginx/wsgi for ceph-rest-api
	@$(INSTALL) -D conf/restapi/cephrestapi.conf \
		$(DESTDIR)/etc/nginx/conf.d/cephrestapi.conf
	@$(INSTALL) -D conf/restapi/cephrestwsgi.py \
		$(DESTDIR)/etc/nginx/cephrestwsgi.py
	# wsgi conf for calamari
	@$(INSTALL) -D conf/calamari.wsgi \
		$(DESTDIR)/opt/calamari/conf/calamari.wsgi
	# wsgi conf for graphite constructed in postinst
	# log dirs for Django apps
	@$(INSTALL) -d $(DESTDIR)/var/log/graphite
	@$(INSTALL) -d $(DESTDIR)/var/log/calamari

install-deb-conf:
	# httpd conf for graphite and calamari vhosts, redhat
	@$(INSTALL) -D conf/httpd/debian/graphite.conf \
		$(DESTDIR)/etc/apache2/sites-available/graphite.conf
	@$(INSTALL) -D conf/httpd/debian/calamari.conf \
		$(DESTDIR)/etc/apache2/sites-available/calamari.conf
	# upstart job for cephrestapi
	@$(INSTALL) -D conf/restapi/init/cephrestapi.conf \
		$(DESTDIR)/etc/init/cephrestapi.conf

install-rh-conf:
	# httpd conf for graphite and calamari vhosts, redhat
	@$(INSTALL) -D conf/httpd/rh/graphite.conf \
		$(DESTDIR)/etc/httpd/conf.d/graphite.conf
	@$(INSTALL) -D conf/httpd/rh/calamari.conf \
		$(DESTDIR)/etc/httpd/conf.d/calamari.conf
	# init job for cephrestapi
	@$(INSTALL) -D conf/restapi/init.d/cephrestapi \
		$(DESTDIR)/etc/init.d/cephrestapi

install-init:
	@echo "install-init"
	@$(INSTALL) -D $(ROOTOG) conf/init/kraken.conf \
		$(DESTDIR)/etc/init/kraken.conf

install-init.d:
	@$(INSTALL) -D $(ROOTOG) conf/carbon/init.d/carbon-cache \
		$(DESTDIR)/etc/init.d/carbon-cache
	@$(INSTALL) -D $(ROOTOG) conf/init.d/kraken \
		$(DESTDIR)/etc/init.d/kraken
	@$(INSTALL) -D $(ROOTOG) conf/init.d/run_loop \
		$(DESTDIR)/etc/init.d/run_loop
	@$(INSTALL) -D $(ROOTOG) conf/restapi/init.d/cephrestapi \
		$(DESTDIR)/etc/init.d/cephrestapi

install-ui:
	@echo "install-ui"
	for d in $(UI_SUBDIRS); do \
		instdir=$$(basename $$d); \
		$(INSTALL) -d $(UI_BASEDIR)/$$instdir; \
		cp -rp $$d/dist/* $(UI_BASEDIR)/$$instdir; \
	done

install-graphite-venv: build-graphite-venv
	@echo "install-graphite-venv"
	$(INSTALL) -d $(DESTDIR)/opt
	cp -a graphite $(DESTDIR)/opt
	# graphite local_settings.py
	@$(INSTALL) -D $(APACHEOG) -m 644 conf/graphite/local_settings.py \
		$(DESTDIR)/opt/graphite/webapp/graphite/local_settings.py

install-calamari-venv: build-calamari-venv
	@echo "install-calamari-venv"
	# copy calamari webapp files into place
	$(INSTALL) -d -m 755 $(DESTDIR)/opt/calamari/webapp
	cp -rp webapp/* $(DESTDIR)/opt/calamari/webapp
	cp -rp calamari/* $(DESTDIR)/opt/calamari

clean:
	for d in $(UI_SUBDIRS); do \
		echo $$d; \
		(cd $$d; \
		if [ -d node_modules ] ; then grunt --no-color clean; fi) \
	done
	@rm -f $(CONFIG_JSON)
	rm -rf graphite
	rm -rf calamari

dist:
	@echo "making dist tarball in $(TARNAME)"
	@for d in $(UI_SUBDIRS); do \
		echo $$d; \
		(cd $$d;  \
		npm install --silent; \
		grunt --no-color saveRevision) \
	done
	@rm -rf $(PKGDIR)
	@$(FINDCMD) | cpio --null -p -d $(PKGDIR)
	@tar -zcf $(TARNAME) $(PKGDIR)
	@rm -rf $(PKGDIR)
	@echo "tar file made in $(TARNAME)"

.PHONY: dist clean build build-venvs build-ui dpkg install install-conf 
.PHONY: install-init install-ui install-graphite-venv install-calamari-venv
