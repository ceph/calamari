INSTALL=/usr/bin/install

build:
	# nothing here

install:
	@$(INSTALL) -D -o root -g root -m 644 conf/diamond/CephCollector.conf $(DESTDIR)/etc/diamond/collectors/CephCollector.conf
	@$(INSTALL) -D -o root -g root -m 644 restapi/cephrestapi.conf $(DESTDIR)/etc/nginx/conf.d/cephrestapi.conf
	@$(INSTALL) -D -o root -g root -m 644 restapi/cephrestwsgi.py $(DESTDIR)/etc/nginx/cephrestwsgi.py

clean:
	@rm -f \
		$(DESTDIR)/etc/diamond/collectors/CephCollector.conf \
		$(DESTDIR)/etc/nginx/conf.d/cephrestapi.conf \
		$(DESTDIR)/etc/nginx/cephrestwsgi.py
