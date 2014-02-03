VERSION=1.0.0
DISTNAMEVER=calamari_$(VERSION)
PKGDIR=calamari-$(VERSION)
TARNAME = ../$(DISTNAMEVER).tar.gz
SRC := $(shell pwd)

INSTALL=/usr/bin/install



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

# add in just the debian files we want
DEBFILES = \
	calamari-server.init \
	calamari-server.docs \
	calamari-server.install \
	calamari-server.postinst \
	calamari-server.prerm \
	calamari-server.postrm \
	changelog \
	compat \
	control \
	copyright \
	rules \
	source/format

venv:
	virtualenv --system-site-packages venv; \

build-venv: venv
	@echo "build-venv"
	set -e; \
	(export PYTHONDONTWRITEBYTECODE=1; \
	cd venv; \
	./bin/python ./bin/pip install \
	  --install-option="--zmq=bundled" \
	  pyzmq>=13.0; \
	./bin/python ./bin/pip install -r \
	  $(SRC)/requirements.production.txt; \
	./bin/python ./bin/pip install --no-install carbon; \
	sed -i 's/== .redhat./== "DONTDOTHISredhat"/' \
		build/carbon/setup.py; \
	./bin/python ./bin/pip install \
	  https://github.com/jcsp/whisper/tarball/calamari; \
	./bin/python ./bin/pip install \
		  --install-option="--prefix=$(SRC)/venv" \
	  --install-option="--install-lib=$(SRC)/venv/lib/python2.7/site-packages" carbon; \
	./bin/python ./bin/pip install \
	  --install-option="--prefix=$(SRC)/venv" \
	  --install-option="--install-lib=$(SRC)/venv/lib/python2.7/site-packages" \
	  https://github.com/jcsp/graphite-web/tarball/calamari; \
	cd ../rest-api ; \
	../venv/bin/python ./setup.py install ; \
	cd ../calamari-web ; \
	../venv/bin/python ./setup.py install ; \
	cd ../cthulhu ; \
	../venv/bin/python ./setup.py install ; \
	cd ../venv ; \
	(find . -type f | xargs grep -l '#!.*'$(SRC) ; \
	   echo bin/activate bin/activate.csh bin/activate.fish ) | \
	while read f; do \
		echo -n "modifying $$f: "; \
		grep $(SRC) $$f; \
		sed -i -e 's;'$(SRC)';/opt/calamari;' $$f; \
	done; \
	if [ -h local/bin ] ; then \
		for p in bin include lib; do \
			rm local/$$p; \
			ln -s /opt/calamari/venv/$$p local/$$p; \
		done; \
	fi)

# this source is just not very amenable to building source packages.
# the Javascript directories don't really go back to "clean"; it might
# be possible to change that, but for now, just skip the source build
dpkg:
	dpkg-buildpackage -b -us -uc

install-common: install-conf install-venv
	@echo "install-common"

install-rpm: install-common install-rh-conf
	@echo "install-rpm"

# for deb
install: install-common install-deb-conf install-salt
	@echo "install"

install-conf: $(CONFFILES)
	@echo "install-conf"
	@$(INSTALL) -D conf/calamari.wsgi \
		$(DESTDIR)/opt/calamari/conf/calamari.wsgi
	@$(INSTALL) -d $(DESTDIR)/etc/supervisor/conf.d
	@$(INSTALL) -D conf/supervisord.production.conf \
		$(DESTDIR)/etc/supervisor/conf.d/calamari.conf
	@$(INSTALL) -d $(DESTDIR)/etc/salt/master.d
	@$(INSTALL) -D conf/salt.master.conf \
		$(DESTDIR)/etc/salt/master.d/calamari.conf
	@$(INSTALL) -d $(DESTDIR)/etc/graphite
	@$(INSTALL) -D conf/carbon/carbon.conf \
		$(DESTDIR)/etc/graphite/carbon.conf
	@$(INSTALL) -D conf/carbon/storage-schemas.conf \
		$(DESTDIR)/etc/graphite/storage-schemas.conf
	# wsgi conf for graphite constructed in postinst
	# log dirs for Django apps
	@$(INSTALL) -d $(DESTDIR)/var/log/graphite
	@$(INSTALL) -d $(DESTDIR)/var/log/calamari
	@$(INSTALL) -d $(DESTDIR)/var/lib/graphite/log/webapp
	@$(INSTALL) -d $(DESTDIR)/var/lib/graphite/whisper
	@$(INSTALL) -d $(DESTDIR)/var/lib/calamari_web
	@$(INSTALL) -d $(DESTDIR)/var/lib/calamari
	@$(INSTALL) -d $(DESTDIR)/var/lib/cthulhu

	@$(INSTALL) -d $(DESTDIR)/etc/calamari
	@$(INSTALL) -D conf/calamari.conf \
		$(DESTDIR)/etc/calamari/calamari.conf

install-salt:
	@$(INSTALL) -d $(DESTDIR)/opt/calamari/salt
	cp -rp salt/srv/* $(DESTDIR)/opt/calamari/salt/

install-deb-conf:
	@echo "install-deb-conf"
	@$(INSTALL) -D conf/httpd/debian/calamari.conf \
		$(DESTDIR)/etc/apache2/sites-available/calamari.conf

install-rh-conf:
	# httpd conf for graphite and calamari vhosts, redhat
	@$(INSTALL) -D conf/httpd/rh/calamari.conf \
		$(DESTDIR)/etc/httpd/conf.d/calamari.conf

install-venv: build-venv
	@echo "install-venv"
	# copy calamari webapp files into place
	$(INSTALL) -d -m 755 $(DESTDIR)/opt/calamari/webapp
	cp -rp webapp/calamari $(DESTDIR)/opt/calamari/webapp
	cp -rp venv $(DESTDIR)/opt/calamari

clean:
	rm -rf venv

dist:
	@echo "making dist tarball in $(TARNAME)"
	@rm -rf $(PKGDIR)
	@$(FINDCMD) | cpio --null -p -d $(PKGDIR)
	@tar -zcf $(TARNAME) $(PKGDIR)
	@rm -rf $(PKGDIR)
	@echo "tar file made in $(TARNAME)"


dev/calamari.conf:
	cd dev/ && python configure.py

rest-api-integration: dev/calamari.conf
	nosetests tests/test_rest_api.py

doc/rest-api/api_examples.json: rest-api-integration
	cp api_examples.json doc/rest-api

rest-api-generated: doc/rest-api/api_examples.json dev/calamari.conf
	cd doc/rest-api && CALAMARI_CONFIG=../../dev/calamari.conf python ../../webapp/calamari/manage.py api_docs

rest-docs: rest-api-generated dev/calamari.conf
	cd doc/rest-api && make html

dev-docs: dev/calamari.conf
	cd doc/development && make html

plugin-docs: dev/calamari.conf
	cd doc/plugin && make html

docs: rest-docs dev-docs

unit-tests: dev/calamari.conf
	CALAMARI_CONFIG=dev/calamari.conf python webapp/calamari/manage.py test rest-api/tests cthulhu/tests

lint:
	echo "Checking code style:" && flake8 cthulhu/ --ignore=E501 && echo "OK"

check: unit-tests lint

.PHONY: dist clean build-venv dpkg install install-conf
.PHONY: build-venv install-venv
