VERSION=0.5.1
DISTNAMEVER=calamari_$(VERSION)
TARNAME = ../$(DISTNAMEVER).tar.gz

INSTALL=/usr/bin/install

UI_SUBDIRS = ui/admin ui/login clients/dashboard
CONFIG_JSON = clients/dashboard/dist/scripts/config.json

CONFFILES = \
	conf/diamond/CephCollector.conf \
	conf/diamond/NetworkCollector.conf \
	restapi/cephrestapi.conf \
	restapi/cephrestwsgi.py

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

DISTFILES:=$(shell $(FINDCMD) | xargs -0 -n 1 | grep -v ' ')
SPACEFILES:=$(shell $(FINDCMD) | xargs -0 -n 1 -I % echo \"%\" | grep ' ')

# add in just the debian files we want
DEBFILES = \
	calamari-agent.install \
	calamari-agent.postinst \
	calamari-agent.prerm \
	calamari-console.init \
	calamari-console.docs \
	calamari-console.install \
	calamari-console.postinst \
	calamari-restapi.install \
	calamari-restapi.postinst \
	calamari-restapi.postrm \
	calamari-restapi.prerm \
	changelog \
	compat \
	control \
	copyright \
	rules \
	source/format

DISTFILES += $(DEBFILES:%=debian/%)

build: build-ui $(CONFIG_JSON) $(CONFFILES)

build-ui:
	@echo "building ui subdirs"
	for d in $(UI_SUBDIRS); do \
		echo $$d; \
		(cd $$d; \
		npm install --silent; \
		bower install; \
		# yes, this is the recommended way to silence grunt \
		grunt build >/dev/null) \
	done

# for right now, this contains one useful thing that should be set
# when running against a live cluster.  We could preinstall it in the
# package or do it in a postinstall; it has more visibility here

$(CONFIG_JSON):
	# XXX ownership?
	echo '{"offline": false}' > $(CONFIG_JSON)

# this source is just not very amenable to building source packages.
# the Javascript directories don't really go back to "clean"; it might
# be possible to change that, but for now, just skip the source build
dpkg: 
	dpkg-buildpackage -b -us -uc

UI_DIRS = ui/admin ui/login clients/dashboard
UI_BASEDIR = $(DESTDIR)/opt/calamari/webapp/content
ROOTOG=-o root -g root -m 644

# a crock; depends on target machine, not build machine. 
# there are more deb-vs-RH dependencies to work out besides this.
WEBUSER:=$(shell egrep 'apache|www-data' /etc/passwd | awk -F: '{print $$1;}')
APACHEOG=-o $(WEBUSER) -g $(WEBUSER) -m 644

install: build $(CONFFILES)
	@echo "installing"
	# Diamond conf files
	@$(INSTALL) -D $(ROOTOG) conf/diamond/CephCollector.conf $(DESTDIR)/etc/diamond/collectors/CephCollector.conf
	@$(INSTALL) -D $(ROOTOG) conf/diamond/NetworkCollector.conf $(DESTDIR)/etc/diamond/collectors/NetworkCollector.conf
	# nginx/wsgi for ceph-rest-api
	@$(INSTALL) -D $(ROOTOG) restapi/cephrestapi.conf $(DESTDIR)/etc/nginx/conf.d/cephrestapi.conf
	@$(INSTALL) -D $(ROOTOG) restapi/cephrestwsgi.py $(DESTDIR)/etc/nginx/cephrestwsgi.py
	# httpd conf for graphite and calamari vhosts, redhat
	@$(INSTALL) -D $(ROOTOG) conf/httpd/rh/graphite.conf $(DESTDIR)/etc/httpd/conf.d/graphite.conf
	@$(INSTALL) -D $(ROOTOG) conf/httpd/rh/calamari.conf $(DESTDIR)/etc/httpd/conf.d/calamari.conf
	# httpd conf for graphite and calamari vhosts, debian
	@$(INSTALL) -D $(ROOTOG) conf/httpd/debian/graphite.conf $(DESTDIR)/etc/apache2/sites-available/graphite.conf
	@$(INSTALL) -D $(ROOTOG) conf/httpd/debian/calamari.conf $(DESTDIR)/etc/apache2/sites-available/calamari.conf
	@$(INSTALL) -d $(ROOTOG) $(DESTDIR)/etc/apache2/sites-enabled
	@ln -s $(DESTDIR)/etc/apache2/sites-available/calamari.conf $(DESTDIR)/etc/apache2/sites-enabled
	@ln -s $(DESTDIR)/etc/apache2/sites-available/graphite.conf $(DESTDIR)/etc/apache2/sites-enabled
	# /etc/init{.d} files
	@$(INSTALL) -D $(ROOTOG) conf/carbon/init.d/carbon-cache $(DESTDIR)/etc/init.d/carbon-cache
	@$(INSTALL) -D $(ROOTOG) conf/upstart/kraken.conf $(DESTDIR)/etc/init/kraken.conf

	# UI code
	for d in $(UI_DIRS); do \
		instdir=$$(basename $$d); \
		$(INSTALL) -d $(UI_BASEDIR)/$$instdir; \
		cp -rp $$d/dist/* $(UI_BASEDIR)/$$instdir; \
	done
	# graphite local_settings.py
	$(INSTALL) -D $(APACHEOG) -m 644 conf/graphite/local_settings.py $(DESTDIR)/opt/graphite/webapp/graphite

clean:
	@rm -f \
		$(DESTDIR)/etc/diamond/collectors/CephCollector.conf \
		$(DESTDIR)/etc/diamond/collectors/NetworkCollector.conf \
		$(DESTDIR)/etc/nginx/conf.d/cephrestapi.conf \
		$(DESTDIR)/etc/nginx/cephrestwsgi.py

	for d in $(UI_SUBDIRS); do \
		echo $$d; \
		(cd $$d; grunt clean > /dev/null) \
	done
	@rm -f $(CONFIG_JSON)


dist:
	@echo "making dist tarball in $(TARNAME)"
	@tar --transform 's;^\./;'$(DISTNAMEVER)'/;' \
		-czf $(TARNAME) $(DISTFILES) $(SPACEFILES) 
	@echo "tar file made in $(TARNAME)"

.PHONY: dist clean build build-ui dpkg install 
