# DEBUG = True
DATABASES = {
    'default': {
        'NAME': '/opt/graphite/storage/graphite.db',
        'ENGINE': 'django.db.backends.sqlite3',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': ''
    }
}
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'log_file': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': '/var/log/graphite/graphite.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['log_file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
