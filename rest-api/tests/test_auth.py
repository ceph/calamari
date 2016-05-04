from django.contrib.auth.models import User
from rest_framework import status
from tests.rest_api_unit_test import RestApiUnitTest


class TestAuthentication(RestApiUnitTest):
    login = False

    # A URI that should require login
    SOMETHING_PRIVILEGED = "/api/v2/grains"

    def test_login(self):
        # I should get a 403 accessing something privileged
        response = self.client.get(self.SOMETHING_PRIVILEGED)
        self.assertStatus(response, status.HTTP_403_FORBIDDEN)

        # I should get a 403 trying to read /user/me
        response = self.client.get("/api/v2/user/me")
        self.assertStatus(response, status.HTTP_403_FORBIDDEN)

        # Now log in with valid credentials
        response = self.client.post("/api/v2/auth/login", {
            'username': self.USERNAME,
            'password': self.PASSWORD
        }, format="json")
        self.assertStatus(response, status.HTTP_200_OK)

        # I should be able to access something privileged
        response = self.client.get(self.SOMETHING_PRIVILEGED)
        self.assertStatus(response, status.HTTP_200_OK)

        # Now log out
        response = self.client.post("/api/v2/auth/logout")
        self.assertStatus(response, status.HTTP_200_OK)

        # I should have lost the ability to access something privileged
        response = self.client.get(self.SOMETHING_PRIVILEGED)
        self.assertStatus(response, status.HTTP_403_FORBIDDEN)


class TestUserChanges(RestApiUnitTest):
    login = True

    def test_change_my_password(self):
        """
        That users can change their own password
        """
        new_password = 'bob'
        self.assertNotEqual(new_password, self.PASSWORD)

        # Do a read-write for PUT
        response = self.client.get("/api/v2/user/me")
        self.assertStatus(response, status.HTTP_200_OK)
        user = response.data
        user['password'] = new_password
        response = self.client.put("/api/v2/user/me", user)
        self.assertStatus(response, status.HTTP_200_OK)

        # Now log out
        response = self.client.post("/api/v2/auth/logout")
        self.assertStatus(response, status.HTTP_200_OK)

        # Try logging in with old password, should fail
        response = self.client.post("/api/v2/auth/login", {
            'username': self.USERNAME,
            'password': self.PASSWORD
        }, format="json")
        self.assertStatus(response, status.HTTP_401_UNAUTHORIZED)

        # Try logging in with new password, should succeed
        response = self.client.post("/api/v2/auth/login", {
            'username': self.USERNAME,
            'password': new_password
        }, format="json")
        self.assertStatus(response, status.HTTP_200_OK)

    def test_change_anothers_password(self):
        """
        That users cannot change one anothers' password.
        """
        stranger = User.objects.create_superuser("stranger", "stranger@admin.com", "stranger_pwd")
        me = User.objects.get(username=self.USERNAME)
        # I can't change his
        response = self.client.patch("/api/v2/user/%s" % stranger.id, {'password': 'new'})
        self.assertStatus(response, status.HTTP_403_FORBIDDEN)

        # But I can change my own
        response = self.client.patch("/api/v2/user/%s" % me.id, {'password': 'new'})
        self.assertStatus(response, status.HTTP_200_OK)
