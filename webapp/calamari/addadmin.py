'''
Run this under the virtualenv python to add the admin user
(or output diagnostics as to why not)
'''
import os
import sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calamari.settings")

from django.contrib.auth.models import User
try:
    User.objects.get(username__exact='admin')
    print "admin user already exists"
except User.DoesNotExist:
    print "creating admin user"
    User.objects.create_superuser('admin', 'calamari@inktank.com', 'admin')
except:
    print >> sys.stderr, "Unexpected exception: ", sys.exc_info()
    sys.exit(1)

sys.exit(0)
