INSTALL=/usr/bin/install

UI_SUBDIRS = ui/admin ui/login clients/dashboard

build:
	@echo "building ui subdirs"
	for d in $(UI_SUBDIRS); do \
		echo $$d; \
		(cd $$d; npm install --silent; bower install; grunt build) \
	done

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

UI_DIRS = ui/admin ui/login clients/dashboard
UI_BASEDIR = $(DESTDIR)/opt/calamari/webapp/content

install: build
	@echo "installing"
	@$(INSTALL) -D -o root -g root -m 644 conf/diamond/CephCollector.conf $(DESTDIR)/etc/diamond/collectors/CephCollector.conf
	@$(INSTALL) -D -o root -g root -m 644 conf/diamond/NetworkCollector.conf $(DESTDIR)/etc/diamond/collectors/NetworkCollector.conf
	@$(INSTALL) -D -o root -g root -m 644 restapi/cephrestapi.conf $(DESTDIR)/etc/nginx/conf.d/cephrestapi.conf
	@$(INSTALL) -D -o root -g root -m 644 restapi/cephrestwsgi.py $(DESTDIR)/etc/nginx/cephrestwsgi.py
	for d in $(UI_DIRS); do \
		instdir=$$(basename $$d); \
		$(INSTALL) -d $(UI_BASEDIR)/$$instdir; \
		cp -rp $$d/dist/* $(UI_BASEDIR)/$$instdir; \
	done

clean:
	@rm -f \
		$(DESTDIR)/etc/diamond/collectors/CephCollector.conf \
		$(DESTDIR)/etc/diamond/collectors/NetworkCollector.conf \
		$(DESTDIR)/etc/nginx/conf.d/cephrestapi.conf \
		$(DESTDIR)/etc/nginx/cephrestwsgi.py

	for d in $(UI_SUBDIRS); do \
		echo $$d; \
		(cd $$d; grunt clean) \
	done

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

.PHONY: dist clean build dpkgs install
