
import argparse
import logging
import os
from django.core.management import execute_from_command_line
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
        if not user_model.filter(username=args.admin_username).exists():
            user_model.objects.create_superuser(
                username=args.admin_username,
                password=args.admin_password,
                email=args.admin_email
            )
    else:
        if not user_model.all().count():
            # When prompting for details, it's good to let the user know what the account
            # is (especially that's a web UI one, not a linux system one)
            log.info("You will now be prompted for login details for the administrative "
                     "user account.  This is the account you will use to log into the web interface "
                     "once setup is complete.")
            # Prompt for user details
            execute_from_command_line(["", "createsuperuser"])


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
