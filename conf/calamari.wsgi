import os
import sys
import site

site.addsitedir('/opt/calamari/venv/lib/python2.6/site-packages')

path = '/opt/calamari/webapp/calamari'
sys.path.append(path)
sys.path.append(path + '/calamari')

os.environ['DJANGO_SETTINGS_MODULE'] = 'calamari.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
