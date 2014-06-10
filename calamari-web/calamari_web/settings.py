# Django settings for calamari project.

import os
from os.path import dirname, abspath, join
import sys
from django.core.exceptions import ImproperlyConfigured

from calamari_common.config import CalamariConfig
config = CalamariConfig()

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
}

try:
    import sqlalchemy  # noqa
except ImportError:
    pass
else:
    DATABASES['default'] = {
        'ENGINE': config.get("calamari_web", "db_engine"),
        'NAME': config.get("calamari_web", "db_name"),
        'USER': config.get("calamari_web", "db_user"),
        'PASSWORD': config.get("calamari_web", "db_password"),
        'HOST': config.get("calamari_web", "db_host"),
        'PORT': config.get("calamari_web", "db_port"),
    }

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

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
STATIC_ROOT = config.get('calamari_web', 'static_root')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = tuple()

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
try:
    SECRET_KEY = open(config.get('calamari_web', 'secret_key_path'), 'r').read()
except IOError:
    # calamari-ctl hasn't been run yet, nothing will work yet.
    SECRET_KEY = ""

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
    'calamari_web.middleware.AngularCSRFRename',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'calamari_web.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'calamari_web.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'calamari_web',
    'rest_framework',
    'calamari_rest'
)

try:
    import graphite  # noqa

    INSTALLED_APPS = INSTALLED_APPS + ('graphite.render',
                                       'graphite.account',
                                       'graphite.metrics',
                                       'graphite.dashboard')
except ImportError:
    graphite = None

try:
    import django_nose  # noqa
except ImportError:
    pass
except ImproperlyConfigured:
    INSTALLED_APPS = INSTALLED_APPS + ('django_nose',)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': "%(asctime)s - %(levelname)s - %(name)s %(message)s"
        }
    },
    'handlers': {
        'log_file': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename':
            config.get('calamari_web', 'log_path'),
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['log_file'],
            'level': config.get('calamari_web', 'log_level'),
            'propagate': True,
        },
    }
}


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
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'calamari_rest.renderers.CalamariBrowsableAPIRenderer',
    )
}

# >>> These settings belong to the graphite app

# Filesystem layout
WEB_DIR = dirname(abspath(__file__))
WEBAPP_DIR = dirname(WEB_DIR)
THIRDPARTY_DIR = join(WEB_DIR, 'thirdparty')
CSS_DIR = ''
CONF_DIR = ''
DASHBOARD_CONF = ''
GRAPHTEMPLATES_CONF = ''
WHITELIST_FILE = ''
INDEX_FILE = ''
WHISPER_DIR = ''
RRD_DIR = ''
DATA_DIRS = []
CLUSTER_SERVERS = []

sys.path.insert(0, WEBAPP_DIR)
# Allow local versions of the libs shipped in thirdparty to take precedence
sys.path.append(THIRDPARTY_DIR)

# Memcache settings
MEMCACHE_HOSTS = []
DEFAULT_CACHE_DURATION = 60  # metric data and graphs are cached for one minute by default
LOG_CACHE_PERFORMANCE = False

# Remote store settings
REMOTE_STORE_FETCH_TIMEOUT = 6
REMOTE_STORE_FIND_TIMEOUT = 2.5
REMOTE_STORE_RETRY_DELAY = 60
REMOTE_FIND_CACHE_DURATION = 300

# Remote rendering settings
REMOTE_RENDERING = False  # if True, rendering is delegated to RENDERING_HOSTS
RENDERING_HOSTS = []
REMOTE_RENDER_CONNECT_TIMEOUT = 1.0
LOG_RENDERING_PERFORMANCE = False

# Miscellaneous settings
CARBONLINK_HOSTS = ["127.0.0.1:7002"]
CARBONLINK_TIMEOUT = 1.0
SMTP_SERVER = "localhost"
DOCUMENTATION_URL = "http://graphite.readthedocs.org/"
ALLOW_ANONYMOUS_CLI = True
LOG_METRIC_ACCESS = False
LEGEND_MAX_ITEMS = 10

# Authentication settings
USE_LDAP_AUTH = False
LDAP_SERVER = ""  # "ldapserver.mydomain.com"
LDAP_PORT = 389
LDAP_SEARCH_BASE = ""  # "OU=users,DC=mydomain,DC=com"
LDAP_BASE_USER = ""  # "CN=some_readonly_account,DC=mydomain,DC=com"
LDAP_BASE_PASS = ""  # "my_password"
LDAP_USER_QUERY = ""  # "(username=%s)"  For Active Directory use "(sAMAccountName=%s)"
LDAP_URI = None

# Required by dashboard app
JAVASCRIPT_DEBUG = False
GRAPHITE_API_PREFIX = "/graphite"

TEMPLATE_DIRS = (os.path.join(config.get('graphite', 'root'),
                              "lib/python2.{pyminor}/site-packages/graphite/templates".format(pyminor=sys.version_info[1])),
                 )
CONTENT_DIR = os.path.join(config.get('graphite', 'root'), "webapp/content/")
if graphite:
    STATICFILES_DIRS = STATICFILES_DIRS + (os.path.join(config.get('graphite', 'root'), "webapp/content/"),)

# <<<

STORAGE_DIR = config.get('graphite', 'storage_path')
LOG_DIR = os.path.dirname(config.get('calamari_web', 'log_path'))
GRAPHITE_ROOT = config.get('graphite', 'root')
# Graphite's build-index.sh expects this to be set in environment
os.environ['GRAPHITE_STORAGE_DIR'] = STORAGE_DIR


# Set config dependent on flags set in local_settings
# Path configuration
if not CONTENT_DIR:
    CONTENT_DIR = join(WEBAPP_DIR, 'content')
if not CSS_DIR:
    CSS_DIR = join(CONTENT_DIR, 'css')

if not CONF_DIR:
    CONF_DIR = os.environ.get('GRAPHITE_CONF_DIR', join(GRAPHITE_ROOT, 'conf'))
if not DASHBOARD_CONF:
    DASHBOARD_CONF = join(CONF_DIR, 'dashboard.conf')
if not GRAPHTEMPLATES_CONF:
    GRAPHTEMPLATES_CONF = join(CONF_DIR, 'graphTemplates.conf')

if not STORAGE_DIR:
    STORAGE_DIR = os.environ.get('GRAPHITE_STORAGE_DIR', join(GRAPHITE_ROOT, 'storage'))
if not WHITELIST_FILE:
    WHITELIST_FILE = join(STORAGE_DIR, 'lists', 'whitelist')
if not INDEX_FILE:
    INDEX_FILE = join(STORAGE_DIR, 'index')
if not LOG_DIR:
    LOG_DIR = join(STORAGE_DIR, 'log', 'webapp')
if not WHISPER_DIR:
    WHISPER_DIR = join(STORAGE_DIR, 'whisper/')
if not RRD_DIR:
    RRD_DIR = join(STORAGE_DIR, 'rrd/')
if not DATA_DIRS:
    DATA_DIRS = [WHISPER_DIR]
