
import argparse
import logging
import os
import subprocess
from django.core.management import execute_from_command_line
import pwd
from cthulhu import config
from cthulhu.persistence import sync_objects
from django.contrib.auth import get_user_model


log = logging.getLogger('calamari_ctl')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
log.addHandler(handler)


def initialize(args):
    """
    This command exists to:

    - Prevent the user having to type more than one thing
    - Prevent the user seeing internals like 'manage.py' which we would
      rather people were not messing with on production systems.
    """
    # Cthulhu's database
    sync_objects.initialize(config.DB_PATH)

    # Django's database
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calamari_web.settings")
    execute_from_command_line(["", "syncdb", "--noinput"])
    user_model = get_user_model()

    if args.admin_username and args.admin_password and args.admin_email:
        if not user_model.objects.filter(username=args.admin_username).exists():
            user_model.objects.create_superuser(
                username=args.admin_username,
                password=args.admin_password,
                email=args.admin_email
            )
    else:
        if not user_model.objects.all().count():
            # When prompting for details, it's good to let the user know what the account
            # is (especially that's a web UI one, not a linux system one)
            log.info("You will now be prompted for login details for the administrative "
                     "user account.  This is the account you will use to log into the web interface "
                     "once setup is complete.")
            # Prompt for user details
            execute_from_command_line(["", "createsuperuser"])

    # Django's static files
    # FIXME: should swallow the output of this, it's super-verbose by default
    execute_from_command_line(["", "collectstatic", "--noinput"])

    # Because we've loaded Django, it will have written log files as
    # this user (probably root).  Fix it so that apache can write them later.
    # FIXME: make www-data username configurable, it'll be different on centos
    # FIXME: put this log file path into calamari config so that we
    # can reason about it without loading django settings.
    # we can know it without having to load settings.py
    apache_user = pwd.getpwnam('www-data')
    from calamari_web.settings import LOGGING, DATABASES
    for log_handler in LOGGING['handlers'].values():
        if 'filename' in log_handler:
            os.chown(log_handler['filename'], apache_user.pw_uid, apache_user.pw_gid)

    # FIXME: this is because of rpc client import importing cthulhu logger :-/ -- should
    # make that not the case or at least get this path from config instead of hardcoding
    from cthulhu.config import LOG_PATH
    os.chown(LOG_PATH, apache_user.pw_uid, apache_user.pw_gid)

    # NB this will cease to be necessary when we switch to postgres by default
    os.chown(DATABASES['default']['NAME'], apache_user.pw_uid, apache_user.pw_gid)

    # Signal supervisor to restart cthulhu as we have created its database
    # TODO: be cleaner by using XMLRPC instead of calling out to subprocess,
    # and don't let user see internal word 'cthulhu'.
    subprocess.call(['supervisorctl', 'restart', 'cthulhu'])

    # TODO: should be generating a SECRET_KEY here for django

    # TODO: optionally generate or install HTTPS certs + hand to apache


def change_password(args):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calamari_web.settings")
    execute_from_command_line(["", "changepassword", args.username])


def main():
    parser = argparse.ArgumentParser(description="""
Calamari setup tool.
    """)

    subparsers = parser.add_subparsers()
    initialize_parser = subparsers.add_parser('initialize',
                                              help="Set up the Calamari server database, and an "
                                                   "initial administrative user account.")
    initialize_parser.add_argument('--admin-username', dest="admin_username",
                                   help="Username for initial administrator account",
                                   required=False)
    initialize_parser.add_argument('--admin-password', dest="admin_password",
                                   help="Password for initial administrator account",
                                   required=False)
    initialize_parser.add_argument('--admin-email', dest="admin_email",
                                   help="Email for initial administrator account",
                                   required=False)
    initialize_parser.set_defaults(func=initialize)

    passwd_parser = subparsers.add_parser('change_password',
                                          help="Reset the password for a Calamari user account")
    passwd_parser.add_argument('username')
    passwd_parser.set_defaults(func=change_password)

    args = parser.parse_args()
    args.func(args)
