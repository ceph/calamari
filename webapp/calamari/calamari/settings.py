# Django settings for calamari project.
import os

from os.path import dirname, abspath, join
import sys

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
# ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

#
# When using sqlite3 db engine for development make sure that an absolute path
# is used to point at the database file. Otherwise the current working
# directory is assumed, and the Kraken service won't be able to find the DB
# without doing a `chdir`. And, we'd rather have this little bit of complexity
# here than there.
#
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             '../db.sqlite3'),
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

APPEND_SLASH = False

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../content/"),
)

STATIC_DOC_ROOT = "/opt/calamari/webapp/content/"
if DEBUG:
    STATIC_DOC_ROOT = "../content"

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'tw8l#w5z%pp41j)zmzzk&b7m(xrn+g_*xco)(pygb13f%*1!$#'

LOGIN_URL = '/login/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
)

CSRF_COOKIE_NAME = "XSRF-TOKEN"
SESSION_COOKIE_NAME = "calamari_sessionid"

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'calamari.middleware.AngularCSRFRename',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'calamari.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'calamari.wsgi.application'

TEMPLATE_DIRS = (
# Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
# Always use forward slashes, even on Windows.
# Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'rest_framework',
    'ceph',
    'graphite.render',
    'graphite.account'
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'log_file': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': '/var/log/calamari/calamari.log'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['log_file'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

if DEBUG:
    LOGGING['handlers']['log_file']['filename'] = "django.log"

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),

    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.HyperlinkedModelSerializer',

    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ]
}

# >>> These settings belong to the graphite app
LOG_DIR = ''
#
## Cluster settings
#CLUSTER_SERVERS = []
#REMOTE_FIND_TIMEOUT = 3.0
#REMOTE_FETCH_TIMEOUT = 6.0
#REMOTE_RETRY_DELAY = 60.0
#REMOTE_READER_CACHE_SIZE_LIMIT = 1000
#CARBONLINK_HOSTS = ["127.0.0.1:7002"]
#CARBONLINK_TIMEOUT = 1.0
#CARBONLINK_HASHING_KEYFUNC = None
#CARBONLINK_RETRY_DELAY = 15
#REPLICATION_FACTOR = 1
#MEMCACHE_HOSTS = []
#FIND_CACHE_DURATION = 300
#FIND_TOLERANCE = 2 * FIND_CACHE_DURATION
#DEFAULT_CACHE_DURATION = 60  # metric data and graphs are cached for one minute by default
#LOG_CACHE_PERFORMANCE = False
#
##Remote rendering settings
#REMOTE_RENDERING = False  # if True, rendering is delegated to RENDERING_HOSTS
#RENDERING_HOSTS = []
#REMOTE_RENDER_CONNECT_TIMEOUT = 1.0
#LOG_RENDERING_PERFORMANCE = False
#
## Remote store settings
#REMOTE_STORE_FETCH_TIMEOUT = 6
#REMOTE_STORE_FIND_TIMEOUT = 2.5
#REMOTE_STORE_RETRY_DELAY = 60
#REMOTE_FIND_CACHE_DURATION = 300
#
##Miscellaneous settings
#SMTP_SERVER = "localhost"
#DOCUMENTATION_URL = "http://graphite.readthedocs.org/"
#ALLOW_ANONYMOUS_CLI = True
#LOG_METRIC_ACCESS = False
#LEGEND_MAX_ITEMS = 10
#RRD_CF = 'AVERAGE'
#
##Authentication settings
#USE_LDAP_AUTH = False
#LDAP_SERVER = ""  # "ldapserver.mydomain.com"
#LDAP_PORT = 389
#LDAP_USE_TLS = False
#LDAP_SEARCH_BASE = ""  # "OU=users,DC=mydomain,DC=com"
#LDAP_BASE_USER = ""  # "CN=some_readonly_account,DC=mydomain,DC=com"
#LDAP_BASE_PASS = ""  # "my_password"
#LDAP_USER_QUERY = ""  # "(username=%s)"  For Active Directory use "(sAMAccountName=%s)"
#LDAP_URI = None

# Filesystem layout
WEB_DIR = dirname( abspath(__file__) )
WEBAPP_DIR = dirname(WEB_DIR)
GRAPHITE_ROOT = dirname(WEBAPP_DIR)
THIRDPARTY_DIR = join(WEB_DIR,'thirdparty')
# Initialize additional path variables
# Defaults for these are set after local_settings is imported
CONTENT_DIR = ''
CSS_DIR = ''
CONF_DIR = ''
DASHBOARD_CONF = ''
GRAPHTEMPLATES_CONF = ''
STORAGE_DIR = ''
WHITELIST_FILE = ''
INDEX_FILE = ''
LOG_DIR = ''
WHISPER_DIR = ''
RRD_DIR = ''
DATA_DIRS = []

CLUSTER_SERVERS = []

sys.path.insert(0, WEBAPP_DIR)
# Allow local versions of the libs shipped in thirdparty to take precedence
sys.path.append(THIRDPARTY_DIR)

# Memcache settings
MEMCACHE_HOSTS = []
DEFAULT_CACHE_DURATION = 60 #metric data and graphs are cached for one minute by default
LOG_CACHE_PERFORMANCE = False

# Remote store settings
REMOTE_STORE_FETCH_TIMEOUT = 6
REMOTE_STORE_FIND_TIMEOUT = 2.5
REMOTE_STORE_RETRY_DELAY = 60
REMOTE_FIND_CACHE_DURATION = 300

#Remote rendering settings
REMOTE_RENDERING = False #if True, rendering is delegated to RENDERING_HOSTS
RENDERING_HOSTS = []
REMOTE_RENDER_CONNECT_TIMEOUT = 1.0
LOG_RENDERING_PERFORMANCE = False

#Miscellaneous settings
CARBONLINK_HOSTS = ["127.0.0.1:7002"]
CARBONLINK_TIMEOUT = 1.0
SMTP_SERVER = "localhost"
DOCUMENTATION_URL = "http://graphite.readthedocs.org/"
ALLOW_ANONYMOUS_CLI = True
LOG_METRIC_ACCESS = False
LEGEND_MAX_ITEMS = 10

#Authentication settings
USE_LDAP_AUTH = False
LDAP_SERVER = "" # "ldapserver.mydomain.com"
LDAP_PORT = 389
LDAP_SEARCH_BASE = "" # "OU=users,DC=mydomain,DC=com"
LDAP_BASE_USER = "" # "CN=some_readonly_account,DC=mydomain,DC=com"
LDAP_BASE_PASS = "" # "my_password"
LDAP_USER_QUERY = "" # "(username=%s)"  For Active Directory use "(sAMAccountName=%s)"
LDAP_URI = None
# <<<

DATA_DIRS = [os.path.join(os.environ['VIRTUAL_ENV'], 'storage')]