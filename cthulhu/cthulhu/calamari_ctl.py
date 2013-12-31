
import argparse
from contextlib import contextmanager
import logging
import os
import sys
from StringIO import StringIO
import subprocess
from django.core.management import execute_from_command_line
import pwd
from django.utils.crypto import get_random_string
from cthulhu.persistence import sync_objects
from django.contrib.auth import get_user_model
from cthulhu.config import CalamariConfig
import string


log = logging.getLogger('calamari_ctl')
log.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
log.addHandler(handler)


@contextmanager
def quiet():
    sys.stdout = StringIO()
    sys.stderr = StringIO()
    try:
        yield
    except:
        log.error(sys.stdout.getvalue())
        log.error(sys.stderr.getvalue())
        raise
    finally:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__


def initialize(args):
    """
    This command exists to:

    - Prevent the user having to type more than one thing
    - Prevent the user seeing internals like 'manage.py' which we would
      rather people were not messing with on production systems.
    """
    log.info("Loading configuration..")
    config = CalamariConfig()

    # Generate django's SECRET_KEY setting
    # Do this first, otherwise subsequent django ops will raise ImproperlyConfigured.
    if not config.get('calamari_web', 'secret_key'):
        config.set_and_write('calamari_web', 'secret_key', get_random_string(50, string.printable))

    # Cthulhu's database
    log.info("Initializing database...")
    sync_objects.initialize(config.get('cthulhu', 'db_path'))

    # Django's database
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calamari_web.settings")
    with quiet():
        execute_from_command_line(["", "syncdb", "--noinput"])

    log.info("Initializing web interface...")
    user_model = get_user_model()

    if args.admin_username and args.admin_password and args.admin_email:
        if not user_model.objects.filter(username=args.admin_username).exists():
            log.info("Creating user '%s'" % args.admin_username)
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
    with quiet():
        execute_from_command_line(["", "collectstatic", "--noinput"])

    # Because we've loaded Django, it will have written log files as
    # this user (probably root).  Fix it so that apache can write them later.
    apache_user = pwd.getpwnam(config.get('calamari_web', 'username'))
    os.chown(config.get('calamari_web', 'log_path'), apache_user.pw_uid, apache_user.pw_gid)

    # Handle SQLite case, otherwise no chown is needed
    if config.get('calamari_web', 'db_engine').endswith("sqlite3"):
        os.chown(config.get('calamari_web', 'db_name'), apache_user.pw_uid, apache_user.pw_gid)

    # Signal supervisor to restart cthulhu as we have created its database
    log.info("Restarting services...")
    subprocess.call(['supervisorctl', 'restart', 'cthulhu'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # TODO: optionally generate or install HTTPS certs + hand to apache
    log.info("Complete.")


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
