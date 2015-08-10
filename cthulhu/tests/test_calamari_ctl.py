import logging
from mock import Mock, patch
from django.test import TestCase

from cthulhu.calamari_ctl import create_admin_users
from cthulhu.calamari_ctl import handler
from django.contrib.auth import get_user_model


handler.setLevel(logging.ERROR)


class TestUser(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch('cthulhu.calamari_ctl.execute_from_command_line')
    def test_that_it_looks_for_existing_users_before_createsuperuser_interactive(self, exe_cmdline):
        args = Mock()
        args.admin_username = False

        User = get_user_model()

        create_admin_users(args)
        print User.objects.all()
        exe_cmdline.assert_called_with(["", "createsuperuser"])

    @patch('cthulhu.calamari_ctl.execute_from_command_line')
    def test_that_does_not_createsuperuser_interactive(self, exe_cmdline):

        args = Mock()
        args.admin_username = False

        User = get_user_model()
        User.objects.create_superuser('superuser', 'superuser', 'superuser@super.org')

        create_admin_users(args)
        self.assertFalse(exe_cmdline.called)

    @patch('cthulhu.calamari_ctl.execute_from_command_line')
    def test_creates_superuser_interactive_when_non_su_present(self, exe_cmdline):
        user_model = get_user_model()
        user_model.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        args = Mock()
        args.admin_username = False
        create_admin_users(args)
        exe_cmdline.assert_called_with(["", "createsuperuser"])
