INSTALL=/usr/bin/install

build:
	# nothing here

CONFFILES = \
	conf/diamond/CephCollector.conf \
	restapi/cephrestapi.conf \
	restapi/cephrestwsgi.py

PKGFILES = \
	debian/changelog \
	debian/compat \
	debian/control \
	debian/copyright\
	debian/inktank-ceph-agent.install \
	debian/inktank-ceph-agent.postinst \
	debian/inktank-ceph-agent.prerm \
	debian/inktank-ceph-restapi.cephrestapi.upstart \
	debian/inktank-ceph-restapi.install \
	debian/inktank-ceph-restapi.postinst \
	debian/inktank-ceph-restapi.postrm \
	debian/inktank-ceph-restapi.prerm \
	debian/rules

dpkg: $(PKGFILES) $(CONFFILES) Makefile
	# XXX don't include ui in the source package yet
	dpkg-buildpackage -Iui -us -uc

install:
	@$(INSTALL) -D -o root -g root -m 644 conf/diamond/CephCollector.conf $(DESTDIR)/etc/diamond/collectors/CephCollector.conf
	@$(INSTALL) -D -o root -g root -m 644 restapi/cephrestapi.conf $(DESTDIR)/etc/nginx/conf.d/cephrestapi.conf
	@$(INSTALL) -D -o root -g root -m 644 restapi/cephrestwsgi.py $(DESTDIR)/etc/nginx/cephrestwsgi.py

clean:
	@rm -f \
		$(DESTDIR)/etc/diamond/collectors/CephCollector.conf \
		$(DESTDIR)/etc/nginx/conf.d/cephrestapi.conf \
		$(DESTDIR)/etc/nginx/cephrestwsgi.py

# unneeded with dpkg as coded above

DISTFILES = \
	bootstrap.sh \
	conf/calamari.conf \
	conf/calamari.wsgi \
	conf/diamond/CephCollector.conf \
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
	tar cf - $(DISTFILES) | gzip -c > ../inktank-ceph_0.1.tar.gz
