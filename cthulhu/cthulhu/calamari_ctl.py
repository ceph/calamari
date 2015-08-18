
import argparse
from contextlib import contextmanager
import json
import logging
import tempfile
import traceback
import os
import sys
from StringIO import StringIO
import subprocess
import pwd
import time

from django.core.management import execute_from_command_line
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model

from calamari_common.config import CalamariConfig

from cthulhu.log import FORMAT

# The log is very verbose by default, filtered at handler level
log = logging.getLogger('calamari_ctl')
log.setLevel(logging.DEBUG)

# The stream handler is what the user sees: don't be too verbose here
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
handler.setLevel(logging.INFO)
log.addHandler(handler)

# The buffer handler is what we dump to a file on failures, be very verbose here
log_buffer = StringIO()
log_tmp = tempfile.NamedTemporaryFile()
buffer_handler = logging.FileHandler(log_tmp.name)
buffer_handler.setFormatter(logging.Formatter(FORMAT))
log.addHandler(buffer_handler)

ALEMBIC_TABLE = 'alembic_version'
POSTGRES_SLS = "/opt/calamari/salt-local/postgres.sls"


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


def _initialize_db(args, config):
    from alembic import command
    from sqlalchemy import create_engine
    from calamari_common.config import AlembicConfig
    from calamari_common.db.base import Base

    # Configure postgres database
    if os.path.exists(POSTGRES_SLS):
        p = subprocess.Popen(["salt-call", "--local", "state.template",
                              POSTGRES_SLS],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        log.debug("Postgres salt stdout: %s" % out)
        log.debug("Postgres salt stderr: %s" % err)
        if p.returncode != 0:
            raise RuntimeError("salt-call for postgres failed with rc={0}".format(p.returncode))
    else:
        # This is the path you take if you're running in a development environment
        log.debug("Skipping postgres configuration, SLS not found")

    # Cthulhu's database
    db_path = config.get('cthulhu', 'db_path')
    engine = create_engine(db_path)
    Base.metadata.reflect(engine)
    alembic_config = AlembicConfig()
    if ALEMBIC_TABLE in Base.metadata.tables:
        log.info("Updating database...")
        # Database already populated, migrate forward
        command.upgrade(alembic_config, "head")
    else:
        log.info("Initializing database...")
        # Blank database, do initial population
        Base.metadata.create_all(engine)
        command.stamp(alembic_config, "head")

    # Django's database
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
    # Write into a file instead of directly, so that package upgrades etc won't spuriously
    # prompt for modified config unless it really is modified.
    if not os.path.exists(config.get('calamari_web', 'secret_key_path')):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        open(config.get('calamari_web', 'secret_key_path'), 'w').write(get_random_string(50, chars))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calamari_web.settings")

    try:
        _initialize_db(args, config)
    except ImportError:
        log.warning("Skipping database configuration")

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


def clear(args):
    from sqlalchemy import create_engine

    if not args.yes_i_am_sure:
        log.warn("This will remove all stored Calamari monitoring status and history.  Use '--yes-i-am-sure' to proceed")
        return

    log.info("Loading configuration..")
    config = CalamariConfig()

    log.info("Dropping tables")
    db_path = config.get('cthulhu', 'db_path')
    engine = create_engine(db_path)
    Base.metadata.drop_all(engine)
    Base.metadata.reflect(engine)
    if ALEMBIC_TABLE in Base.metadata.tables:
        Base.metadata.tables[ALEMBIC_TABLE].drop(engine)
    log.info("Complete.  Now run `%s initialize`" % os.path.basename(sys.argv[0]))


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

    clear_parser = subparsers.add_parser('clear', help="Clear the Calamari database")
    clear_parser.add_argument('--yes-i-am-sure', dest="yes_i_am_sure", action='store_true', default=False)
    clear_parser.set_defaults(func=clear)

    args = parser.parse_args()

    try:
        args.func(args)
    except:
        debug_filename = "/tmp/{0}.txt".format(time.strftime("%Y-%m-%d_%H%M", time.gmtime()))
        open(debug_filename, 'w').write(json.dumps({
            'argv': sys.argv,
            'log': open(log_tmp.name, 'r').read(),
            'backtrace': traceback.format_exc()
        }, indent=2))
        log.error("We are sorry, an unexpected error occurred.  Debugging information has\n"
                  "been written to a file at '{0}', please include this when seeking technical\n"
                  "support.".format(debug_filename))
