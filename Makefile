INSTALL=/usr/bin/install

UI_SUBDIRS = ui/admin ui/login clients/dashboard
CONFIG_JSON = clients/dashboard/dist/scripts/config.json

CONFFILES = \
	conf/diamond/CephCollector.conf \
	conf/diamond/NetworkCollector.conf \
	restapi/cephrestapi.conf \
	restapi/cephrestwsgi.py

PKGFILES = \
	debian/changelog \
	debian/compat \
	debian/control \
	debian/copyright\
	debian/calamari-agent.install \
	debian/calamari-agent.postinst \
	debian/calamari-agent.prerm \
	debian/calamari-restapi.install \
	debian/calamari-restapi.postinst \
	debian/calamari-restapi.postrm \
	debian/calamari-restapi.prerm \
	debian/rules

dpkg: $(PKGFILES) $(CONFFILES) Makefile
	dpkg-buildpackage -us -uc
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
	# httpd conf for graphite and calamari vhosts
	@$(INSTALL) -D $(ROOTOG) conf/graphite/graphite.conf $(DESTDIR)/etc/httpd/conf.d/graphite.conf
	@$(INSTALL) -D $(ROOTOG) conf/calamari.conf $(DESTDIR)/etc/httpd/conf.d/calamari.conf
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

# unneeded with dpkg as coded above

DISTFILES = \
	bootstrap.sh \
	conf/calamari.conf \
	conf/calamari.wsgi \
	conf/diamond/CephCollector.conf \
	conf/diamond/NetworkCollector.conf \
	conf/upstart/kraken.conf \
	doc/annotated.clicmds \
	doc/calamari-api.md \
	doc/calamari-client-examples.md \
	doc/deploy.md \
	Makefile \
	packaging.design.notes \
	README.md \
	requirements.txt \
	restapi/cephrestapi.conf \
	restapi/cephrestwsgi.py \
	restapi/init/cephrestapi.conf \
	restapi/init.d/cephrestapi \
	restapi/uwsgi.startup \
	ui.build.instructions \
	Vagrantfile \
	webapp/calamari/calamari/__init__.py \
	webapp/calamari/calamari/middleware.py \
	webapp/calamari/calamari/settings.py \
	webapp/calamari/calamari/urls.py \
	webapp/calamari/calamari/views.py \
	webapp/calamari/calamari/wsgi.py \
	webapp/calamari/ceph/fixtures/ceph_fake.json \
	webapp/calamari/ceph/__init__.py \
	webapp/calamari/ceph/management/commands/ceph_refresh.py \
	webapp/calamari/ceph/management/commands/__init__.py \
	webapp/calamari/ceph/management/__init__.py \
	webapp/calamari/ceph/models.py \
	webapp/calamari/ceph/serializers.py \
	webapp/calamari/ceph/tests.py \
	webapp/calamari/ceph/urls.py \
	webapp/calamari/ceph/views.py \
	webapp/calamari/.gitignore \
	webapp/calamari/manage.py

dist:
	tar cf - $(DISTFILES) | gzip -c > ../calamari_0.1.tar.gz

.PHONY: dist clean build build-ui dpkg install 
