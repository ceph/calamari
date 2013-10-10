import os
import sys
import site

prev_sys_path = list(sys.path)
site.addsitedir('/opt/calamari/venv/lib/python2.6/site-packages')

# Reorder sys.path so new directories at the front.
new_sys_path = []
for item in list(sys.path):
    if item not in prev_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)
sys.path[:0] = new_sys_path

path = '/opt/calamari/webapp/calamari'
sys.path.append(path)
sys.path.append(path + '/calamari')

os.environ['DJANGO_SETTINGS_MODULE'] = 'calamari.settings'

# The commented out Python below is used for the WSGI authentication on static
# directories being served by Apache. See notes in calamari.conf about how it
# might be used depending on what solution we come up with to do static
# serving + auth.

#from django import db
#from django.conf import settings
#from django.contrib.sessions.backends.db import SessionStore
#from django.contrib.auth.models import User
#from django.core.handlers.wsgi import WSGIRequest
#from django.core.handlers.base import BaseHandler
#
#class AccessHandler(BaseHandler):
#    def __call__(self, request):
#        from django.conf import settings
#        # set up middleware
#        if self._request_middleware is None:
#            self.load_middleware()
#	# apply the middleware to it
#	# actually only session and auth middleware would be needed here
#	for middleware_method in self._request_middleware:
#		middleware_method(request)
#	return request
#
#def allow_access(environ, host):
#    """
#    Authentication handler that checks if user is logged in
#    """
#
#    # Fake this, allow_access gets a stripped environ
#    environ['wsgi.input'] = None
#
#    request = WSGIRequest(environ)
#    errors = environ['wsgi.errors']
#    request = AccessHandler()(request)
#    
#    try:
#	if request.user.is_authenticated():
#            return True
#        else:
#            return False
#    except Exception as e:
#        errors.write('Exception: %s\n' % e)
#        return False
#
#    finally:
#        db.connection.close()

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
