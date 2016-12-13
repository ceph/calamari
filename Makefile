VERSION ?= $(shell ./get-versions.sh VERSION)
REVISION ?= $(shell ./get-versions.sh REVISION)
DIST ?= unstable
DCH_VERSION=$(shell git describe | sed 's/^v//')
PACKAGE_VERSION ?= 1
CODENAME ?= $(shell lsb_release -sc)
# You must set BPTAG when DCH_VERSION does not match a git tag
BPTAG ?= "" # ~bpoNN+M where NN is the Debian major version and M is the 'package revision'
DEBEMAIL ?= dmick@redhat.com
FLAVOR ?= $(shell ./get-flavor.sh)

# debian upstream tarballs: {name}_{version}.orig.tar.gz
# rpm tarball names: apparently whatever you name in Source0, but
# {name}_{version}.tar.gz will work
DISTNAMEVER=calamari-server_$(VERSION)
# PKGDIR is the directory the tarball is made from/unpacks to, and needs
# - before version
PKGDIR=calamari-server-$(VERSION)
TARNAME = ../$(DISTNAMEVER).tar.gz
SRC := $(shell pwd)

INSTALL=/usr/bin/install

all: build

build: version build-venv

DATESTR=$(shell /bin/echo -n "built on "; date)
set_deb_version:
	@echo "target: $@"
	if [ "$(shell lsb_release -si)" = "Ubuntu" ] ; then \
		DEBEMAIL=$(DEBEMAIL) dch \
			--newversion $(DCH_VERSION)-$(PACKAGE_VERSION)$(CODENAME) \
			-D $(DIST) --force-bad-version --force-distribution "$(DATESTR)" ; \
	else \
		DEBEMAIL=$(DEBEMAIL) dch \
			--newversion $(DCH_VERSION)$(BPTAG) \
			-D $(DIST) --force-bad-version --force-distribution "$(DATESTR)" ; \
	fi

venv:
	if [ ! -d $(SRC)/venv ] ; then \
		virtualenv --system-site-packages $(SRC)/venv ; \
	fi


VERSION_PY = rest-api/calamari_rest/version.py
version: $(VERSION_PY)

$(VERSION_PY):
	@echo "target: $@"
	echo "VERSION = \"$(VERSION)-$(REVISION)$(BPTAG)\"" > $(VERSION_PY)

# separate targets exist below for debugging; the expected order is
# "venv -> build-venv-carbon/build-venv-reqs -> fixup-venv"

build-venv: fixup-venv

# try for idempotency with pip freeze | grep carbon
build-venv-carbon: venv
	@echo "target: $@"
	set -ex; \
	(export PYTHONDONTWRITEBYTECODE=1; \
	cd venv; \
	pyver=$$(./bin/python -c 'import sys; print "{0}.{1}".format(sys.version_info[0], sys.version_info[1])') ; \
	if ! ./bin/python ./bin/pip freeze | grep -s -q carbon ; then \
		./bin/python ./bin/pip install --no-install carbon; \
		sed -i 's/== .redhat./== "DONTDOTHISredhat"/' \
			build/carbon/setup.py; \
		./bin/python ./bin/pip install --no-download \
		  --install-option="--prefix=$(SRC)/venv" \
		  --install-option="--install-lib=$(SRC)/venv/lib/python$${pyver}/site-packages" carbon; \
	fi \
	)

build-venv-reqs: venv
	@echo "target: $@"
	set -ex; \
	(export PYTHONDONTWRITEBYTECODE=1; \
	cd venv; \
	pyver=$$(./bin/python -c 'import sys; print "{0}.{1}".format(sys.version_info[0], sys.version_info[1])') ; \
	./bin/python ./bin/pip install \
	  --install-option="--zmq=bundled" \
	  'pyzmq==14.2.0' && \
	./bin/python ./bin/pip install \
	  https://github.com/graphite-project/whisper/tarball/a6e2176e && \
	./bin/python ./bin/pip install -r \
	  $(SRC)/requirements/$${pyver}/requirements.production.txt && \
	./bin/python ./bin/pip install -I -r \
	  $(SRC)/requirements/$${pyver}/requirements.production.force.txt && \
	./bin/python ./bin/pip install \
	  --install-option="--prefix=$(SRC)/venv" \
	  --install-option="--install-lib=$(SRC)/venv/lib/python$${pyver}/site-packages" \
	  https://github.com/ceph/graphite-web/tarball/calamari && \
	cd ../calamari-common ; \
	../venv/bin/python ./setup.py install && \
	cd ../rest-api ; \
	../venv/bin/python ./setup.py install && \
	cd ../calamari-web ; \
	../venv/bin/python ./setup.py install && \
	cd ../cthulhu ; \
	../venv/bin/python ./setup.py install && \
	cd ../venv ; )

fixup-venv: build-venv-carbon build-venv-reqs
	@echo "target: $@"
	set -x; \
	cd venv; \
	fixfiles=$$(find -type f -not -name *.py[cox] -exec grep -Il \#!.*$(SRC) {} \;) ; \
	echo "fixfiles: $$fixfiles" ; \
	fixfiles="$$fixfiles bin/activate*" ; \
	echo "fixfiles: $$fixfiles" ; \
	for f in $$fixfiles; do \
		echo -n "fixing path in $$f: "; \
		grep $(SRC) "$$f"; \
		sed -i -e 's;'$(SRC)';/opt/calamari;' "$$f"; \
	done; \
	if [ -h local/bin ] ; then \
		for p in bin include lib; do \
			rm local/$$p; \
			ln -s /opt/calamari/venv/$$p local/$$p; \
		done; \
	fi

# when this repo contained the Javascript code, it was difficult to make
# source packages work right; it might be easier now
dpkg: set_deb_version
	@echo "target: $@"
	dpkg-buildpackage -b -us -uc

install-common: install-conf install-venv install-salt install-alembic install-scripts
	@echo "target: $@"

install-rpm: build install-common install-rh-conf
	@echo "target: $@"

# for deb
install: build
	@echo "target: $@"
	@if [ -z "$(DESTDIR)" ] ; then echo "must set DESTDIR"; exit 1; \
		else $(MAKE) install_real ; fi

install_real: build install-common install-deb-conf
	@echo "target: $@"

install-conf: $(CONFFILES)
	@echo "target: $@"
	@$(INSTALL) -D -m 0644 conf/calamari.wsgi \
		$(DESTDIR)/opt/calamari/conf/calamari.wsgi
	@$(INSTALL) -d $(DESTDIR)/etc/supervisor/conf.d
	@$(INSTALL) -D -m 0644 conf/supervisord.production.conf \
		$(DESTDIR)/etc/supervisor/conf.d/calamari.conf
	@$(INSTALL) -d $(DESTDIR)/etc/salt/master.d
	@$(INSTALL) -D -m 0644 conf/salt.master.conf \
		$(DESTDIR)/etc/salt/master.d/calamari.conf
	@$(INSTALL) -d $(DESTDIR)/etc/graphite
	@$(INSTALL) -D -m 0644 conf/carbon/carbon.conf \
		$(DESTDIR)/etc/graphite/carbon.conf
	@$(INSTALL) -D -m 0644 conf/carbon/storage-schemas.conf \
		$(DESTDIR)/etc/graphite/storage-schemas.conf
	# wsgi conf for graphite constructed in postinst
	# log dirs for Django apps
	@$(INSTALL) -d $(DESTDIR)/var/log/graphite
	@$(INSTALL) -d $(DESTDIR)/var/log/calamari
	@$(INSTALL) -d $(DESTDIR)/var/lib/graphite/log/webapp
	@$(INSTALL) -d $(DESTDIR)/var/lib/graphite/whisper
	@$(INSTALL) -d $(DESTDIR)/var/lib/calamari
	@$(INSTALL) -d $(DESTDIR)/var/lib/cthulhu

	@$(INSTALL) -d $(DESTDIR)/etc/calamari
	@$(INSTALL) -D -m 0644 conf/calamari/$(FLAVOR)/calamari.conf \
		$(DESTDIR)/etc/calamari/calamari.conf
	@$(INSTALL) -D -m 0644 conf/alembic.ini \
		$(DESTDIR)/etc/calamari/alembic.ini
	@$(INSTALL) -d $(DESTDIR)/etc/logrotate.d
	@$(INSTALL) -D -m 0644 conf/logrotate.d/calamari \
	    $(DESTDIR)/etc/logrotate.d/calamari

install-salt:
	@echo "target: $@"
	@$(INSTALL) -d $(DESTDIR)/opt/calamari/salt
	cp -rp salt/srv/* $(DESTDIR)/opt/calamari/salt/
	@$(INSTALL) -d $(DESTDIR)/opt/calamari/salt-local
	cp -rp salt/local/*.sls $(DESTDIR)/opt/calamari/salt-local

install-alembic:
	@echo "target: $@"
	@$(INSTALL) -d $(DESTDIR)/opt/calamari/alembic
	cp -rp alembic/* $(DESTDIR)/opt/calamari/alembic

install-deb-conf:
	@echo "target: $@"
	@$(INSTALL) -D conf/httpd/calamari.conf \
		$(DESTDIR)/etc/apache2/sites-available/calamari.conf

install-rh-conf:
	@echo "target: $@"
	# add WSGISocketPrefix, see:
	# http://code.google.com/p/modwsgi/wiki/ConfigurationDirectives#WSGISocketPrefix
	@$(INSTALL) -D conf/httpd/calamari.conf \
		$(DESTDIR)/etc/httpd/conf.d/calamari.conf
	@sed -i '1iWSGISocketPrefix run/wsgi' $(DESTDIR)/etc/httpd/conf.d/calamari.conf

install-venv:
	@echo "target: $@"
	# copy calamari webapp files into place
	$(INSTALL) -d -m 755 $(DESTDIR)/opt/calamari/webapp
	cp -rp webapp/calamari $(DESTDIR)/opt/calamari/webapp
	cp -rp venv $(DESTDIR)/opt/calamari

install-scripts: install-venv
	@echo "target: $@"
	# Link our scripts from the virtualenv into the global PATH
	$(INSTALL) -d $(DESTDIR)/usr/bin
	ln -s ../../opt/calamari/venv/bin/calamari-ctl $(DESTDIR)/usr/bin/

clean:
	@echo "target: $@"
	rm -rf venv $(VERSION_PY)

# Strategy for building dist tarball: find what we know is source
# want in sources.

FIND_TOPLEVEL = "find . -maxdepth 1 -type f -not -name .gitignore -print0"
FIND_RECURSE = "find alembic calamari-common calamari-web conf cthulhu doc requirements repobuild rest-api salt tests webapp selinux -print0"

dist:
	@echo "target: $@"
	@echo "making dist tarball in $(TARNAME)"
	@rm -rf $(PKGDIR)
	@eval "$(FIND_TOPLEVEL); $(FIND_RECURSE)" | cpio --null -p -d $(PKGDIR)
	@tar -zcf $(TARNAME) $(PKGDIR)
	@rm -rf $(PKGDIR)
	@echo "tar file made in $(TARNAME)"


dev/calamari.conf:
	@echo "target: $@"
	cd dev/ && python configure.py

# prefer the local version of nosetests, but allow system version
rest-api-integration: dev/calamari.conf
	@echo "target: $@"
	if [ -n "$$VIRTUAL_ENV" ] && [ -x $$VIRTUAL_ENV/bin/nosetests ] ; then \
		CALAMARI_CONFIG=dev/calamari.conf nosetests tests/test_rest_api.py:TestApi.test_touch_urls; \
	else \
		CALAMARI_CONFIG=dev/calamari.conf python $$(which nosetests) tests/test_rest_api.py ; \
	fi

doc/calamari_rest/resources/api_examples.json: rest-api-integration
	@echo "target: $@"
	cp api_examples.json doc/calamari_rest/resources

rest-api-generated: doc/calamari_rest/resources/api_examples.json dev/calamari.conf
	@echo "target: $@"
	cd doc/calamari_rest/resources && CALAMARI_CONFIG=../../../dev/calamari.conf python ../../../webapp/calamari/manage.py api_docs

docs: rest-api-generated
	cd doc && make html

unit-tests: dev/calamari.conf
	@echo "target: $@"
	CALAMARI_CONFIG=dev/calamari.conf python webapp/calamari/manage.py test --noinput rest-api/tests cthulhu/tests

lint:
	@echo "target: $@"
	echo "Checking code style:" && \
		flake8 cthulhu/ --ignore=E501,E402,E731 &&\
		flake8 rest-api/ --ignore=E501,E402,E731 &&\
		flake8 calamari-common/ --ignore=E501,E402,E731 &&\
		flake8 calamari-web/ --ignore=E501,E402,E731 &&\
		flake8 tests/ --ignore=E501,E402,E731 &&\
		flake8 salt/srv/salt/ --ignore=E501,E402,E731 &&\
		echo "OK"

check: unit-tests lint

.PHONY: dist clean build-venv dpkg install install-conf
.PHONY: install-venv set-deb-version version
