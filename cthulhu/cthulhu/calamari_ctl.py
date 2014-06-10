
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
from django.core.exceptions import ObjectDoesNotExist
import pwd
import time

from django.core.management import execute_from_command_line
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model

from calamari_common.db.base import Base
from calamari_common.config import CalamariConfig, AlembicConfig

# Import sqlalchemy objects so that create_all sees them
from cthulhu.persistence.sync_objects import SyncObject  # noqa
from cthulhu.persistence.servers import Server, Service  # noqa
from calamari_common.db.event import Event  # noqa
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
SERVICES_SLS = "/opt/calamari/salt-local/services.sls"
RELAX_SALT_PERMS_SLS = "/opt/calamari/salt-local/relax_salt_perms.sls"


class CalamariUserError(Exception):
    pass


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


<<<<<<< HEAD
def run_local_salt(sls, message):
    # Configure postgres database
    if os.path.exists(sls):
        log.info("Starting/enabling {message}...".format(message=message))
        p = subprocess.Popen(["salt-call", "--local", "state.template",
                              sls],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        log.debug("{message} salt stdout: {out}".format(message=message, out=out))
        log.debug("{message} salt stderr: {err}".format(message=message, err=err))
        if p.returncode != 0:
            raise RuntimeError("salt-call for {message} failed with rc={rc}".format(message=message, rc=p.returncode))
    else:
        # This is the path you take if you're running in a development environment
        log.debug("Skipping {message} configuration, SLS not found".format(message=message))


def create_default_roles():
    from django.contrib.auth.models import Group
    Group.objects.get_or_create(name='readonly')
    Group.objects.get_or_create(name='read/write')


def assign_role(args):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calamari_web.settings")
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import Group
    user_model = get_user_model()
    try:
        user = user_model.objects.get(username=args.username)
    except user_model.DoesNotExist, e:
        log.error('User %s does not exist' % args.username)
        raise CalamariUserError(str(e))

    user.groups = []
    user.is_superuser = False

    if args.role_name == 'superuser':
        user.is_superuser = True
    else:
        try:
            role = Group.objects.get(name=args.role_name)
        except ObjectDoesNotExist, e:
            log.error('Role %s does not exist' % args.role_name)
            raise CalamariUserError(str(e))

        user.groups.add(role)

    user.save()


def add_user(args):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calamari_web.settings")
    from django.db import IntegrityError
    from django.contrib.auth import get_user_model
    user_model = get_user_model()
    try:
        user_model.objects.create_user(args.username, args.email, args.password)
    except IntegrityError, e:
        log.error('User with username %s already exists' % args.username)
        raise CalamariUserError(str(e))

    args.role_name = 'read/write'
    assign_role(args)


def disable_user(args):
    change_user_active_status(args.username, False)


def enable_user(args):
    change_user_active_status(args.username, True)


def change_user_active_status(username, active):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calamari_web.settings")
    from django.db import IntegrityError
    from django.contrib.auth import get_user_model
    user_model = get_user_model()
    try:
        user = user_model.objects.get(username=username)
        user.is_active = active
        user.save()
    except IntegrityError, e:
        log.error('User with username %s cannot be deleted' % username)
        raise CalamariUserError(str(e))


def create_admin_users(args):
    from django.contrib.auth import get_user_model
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
        if not user_model.objects.filter(is_superuser=True).count():
            # When prompting for details, it's good to let the user know what the account
            # is (especially that's a web UI one, not a linux system one)
            log.info("You will now be prompted for login details for the administrative "
                     "user account.  This is the account you will use to log into the web interface "
                     "once setup is complete.")
            # Prompt for user details
            execute_from_command_line(["", "createsuperuser"])


def update_connected_minions():
    from cthulhu.manager import config
    from calamari_common.salt_wrapper import Key, master_config
    if len(Key(master_config(config.get('cthulhu', 'salt_config_path'))).list_keys()['minions']) == 0:
        # no minions to update
        return

    message = "Updating already connected nodes."
    log.info(message)
    p = subprocess.Popen(["salt", "*", "state.highstate"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    log.debug("{message} salt stdout: {out}".format(message=message, out=out))
    log.debug("{message} salt stderr: {err}".format(message=message, err=err))
    if p.returncode != 0:
        raise RuntimeError("{message} failed with rc={rc}".format(message=message, rc=p.returncode))


def _initialize_db(args, config):
    from alembic import command
    from sqlalchemy import create_engine

    run_local_salt(sls=RELAX_SALT_PERMS_SLS, message='salt')
    run_local_salt(sls=POSTGRES_SLS, message='postgres')

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

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calamari_web.settings")

    # Django's database
    with quiet():
        execute_from_command_line(["", "syncdb", "--noinput"])

    create_default_roles()
    create_admin_users(args)
    log.info("Initializing web interface...")


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

    # Start services, configure to run on boot
    run_local_salt(sls=SERVICES_SLS, message='services')

    # During an upgrade: update minions that were connected previously
    update_connected_minions()

    # Signal supervisor to restart cthulhu as we have created its database
    log.info("Restarting services...")
    subprocess.call(['supervisorctl', 'restart', 'cthulhu'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # TODO: optionally generate or install HTTPS certs + hand to apache
    log.info("Complete.")


def change_password(args):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calamari_web.settings")
    if args.password:
        from django.contrib.auth import get_user_model
        user_model = get_user_model()
        try:
            user = user_model.objects.get(username=args.username)
            user.set_password(args.password)
            user.save()
        except user_model.DoesNotExist:
            log.error("User '%s' does not exist." % args.username)
    else:
        execute_from_command_line(["", "changepassword", args.username])


def rename_user(args):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "calamari_web.settings")
    from django.contrib.auth import get_user_model
    user_model = get_user_model()
    try:
        user_model.objects.get(username=args.new_username)
        log.error("New username '%s' is already in use." % args.new_username)
    except user_model.DoesNotExist:
        try:
            user = user_model.objects.get(username=args.username)
            user.username = args.new_username
            user.save()
        except user_model.DoesNotExist:
            log.error("User '%s' does not exist." % args.username)


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


def add_user_subparser(subparsers, func, help_text):
    """
    Parameterize subparsers that require a positional username argument
    """
    user_parser = subparsers.add_parser(func.__name__, help=help_text)
    user_parser.set_defaults(func=func)
    user_parser.add_argument('username')
    return user_parser


def main():
    parser = argparse.ArgumentParser(description="""
Calamari setup tool.
    """)

    parser.add_argument('--devmode',
                        dest="devmode",
                        action='store_true',
                        default=False,
                        help="signals that we don't need root privileges to run",
                        required=False)

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

    add_user_parser = add_user_subparser(subparsers, add_user, "Create user accounts")
    add_user_parser.add_argument('--password', dest="password",
                                 help="Password for account",
                                 required=False)
    add_user_parser.add_argument('--email', dest="email",
                                 help="Email for account",
                                 required=True)

    assign_role_parser = add_user_subparser(subparsers, assign_role, "Assign a role to an existing user")
    assign_role_parser.add_argument('--role', dest="role_name",
                                    help="Role to assign to user, one of readonly, read/write, superuser",
                                    required=True)

    passwd_parser = add_user_subparser(subparsers, change_password, "Reset the password for a Calamari user account")
    passwd_parser.add_argument('--password', dest="password",
                               help="New password",
                               required=False)
    add_user_subparser(subparsers, disable_user, "Disable a user")
    add_user_subparser(subparsers, enable_user, "Enable a user")

    rename_parser = add_user_subparser(subparsers, rename_user, "Rename a user")
    rename_parser.add_argument('new_username')

    clear_parser = subparsers.add_parser('clear', help="Clear the Calamari database")
    clear_parser.add_argument('--yes-i-am-sure', dest="yes_i_am_sure", action='store_true', default=False)
    clear_parser.set_defaults(func=clear)

    args = parser.parse_args()

    try:
        if args.devmode or os.geteuid() == 0:
            args.func(args)
        else:
            log.error('Need root privileges to run')
    except Exception, e:
        if args.func in (assign_role, add_user) and isinstance(e, CalamariUserError):
            sys.exit(1)

        log.error(str(e))
        debug_filename = "/tmp/{0}.txt".format(time.strftime("%Y-%m-%d_%H%M", time.gmtime()))
        open(debug_filename, 'w').write(json.dumps({
            'argv': sys.argv,
            'log': open(log_tmp.name, 'r').read(),
            'backtrace': traceback.format_exc()
        }, indent=2))
        log.error("We are sorry, an unexpected error occurred.  Debugging information has\n"
                  "been written to a file at '{0}', please include this when seeking technical\n"
                  "support.".format(debug_filename))
