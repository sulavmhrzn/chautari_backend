from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.authentication.models import Profile, User


class UserModelTest(TestCase):
    def setUp(self):
        self.User = get_user_model()

    def test_create_user(self):
        """Test creating a regular user"""
        user = self.User.objects.create_user(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            password="testpass123",
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")
        self.assertTrue(user.check_password("testpass123"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertFalse(user.email_verified)

    def test_create_superuser(self):
        """Test creating a superuser"""
        admin_user = self.User.objects.create_superuser(
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            password="adminpass123",
        )
        self.assertEqual(admin_user.email, "admin@example.com")
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_active)

    def test_create_user_without_email_raises_error(self):
        """Test creating user without email raises ValueError"""
        with self.assertRaises(ValueError):
            self.User.objects.create_user(
                email="", first_name="John", last_name="Doe", password="testpass123"
            )

    def test_create_superuser_with_invalid_flags(self):
        """Test creating superuser with invalid is_staff/is_superuser flags"""
        with self.assertRaises(ValueError):
            self.User.objects.create_superuser(
                email="admin@example.com",
                first_name="Admin",
                last_name="User",
                password="adminpass123",
                is_staff=False,
            )

    def test_email_normalization(self):
        """Test email normalization"""
        user = self.User.objects.create_user(
            email="Test@EXAMPLE.COM",
            first_name="John",
            last_name="Doe",
            password="testpass123",
        )
        self.assertEqual(user.email, "Test@example.com")


class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            password="testpass123",
        )

    def test_profile_is_created(self):
        """Test profile creation"""
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.user, self.user)
        self.assertIsNone(profile.phone_number)
        self.assertFalse(profile.is_phone_number_verified)

    def test_profile_string_representation(self):
        """Test profile string representation"""
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(str(profile), self.user.email)

    def test_profile_cascade_delete(self):
        """Test profile is deleted when user is deleted"""
        profile = Profile.objects.get(user=self.user)
        user_id = self.user.id
        profile_id = profile.id

        self.user.delete()

        self.assertFalse(User.objects.filter(id=user_id).exists())
        self.assertFalse(Profile.objects.filter(id=profile_id).exists())


class SignUpViewTest(APITestCase):
    def setUp(self):
        self.signup_url = reverse("signup")
        self.valid_payload = {
            "email": "test@swsc.edu.np",
            "first_name": "John",
            "last_name": "Doe",
            "password": "sulavmhrzn",
        }

    def test_signup_success(self):
        """Test successful user signup"""
        response = self.client.post(self.signup_url, self.valid_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertIn("data", response.data)
        self.assertEqual(response.data["data"]["email"], "test@swsc.edu.np")
        self.assertEqual(response.data["data"]["first_name"], "John")
        self.assertEqual(response.data["data"]["last_name"], "Doe")
        self.assertNotIn("password", response.data["data"])

    def test_signup_invalid_data(self):
        """Test signup with invalid data"""
        invalid_payload = {
            "email": "invalid-email",
            "first_name": "",
            "last_name": "Doe",
            "password": "123",
        }
        response = self.client.post(self.signup_url, invalid_payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("error", response.data)

    def test_signup_invalid_email_domain(self):
        """Test signup with invalid data"""
        invalid_payload = {
            "email": "test@example.com",
            "first_name": "test",
            "last_name": "Doe",
            "password": "sulavmhrzn",
        }
        response = self.client.post(self.signup_url, invalid_payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("error", response.data)
        self.assertIn("email", response.data["error"])
        self.assertIn("not a valid college email", response.data["error"]["email"])

    def test_signup_duplicate_email(self):
        """Test signup with existing email"""
        # Create a user first
        User.objects.create_user(
            email="test@swsc.edu.np",
            first_name="Existing",
            last_name="User",
            password="password123",
        )

        response = self.client.post(self.signup_url, self.valid_payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])


class CurrentUserViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@swsc.edu.np",
            first_name="John",
            last_name="Doe",
            password="password123",
        )
        self.user.profile.phone_number = "+9779841234567"
        self.profile = self.user.profile.save()
        self.current_user_url = reverse("current_user")  # Add this URL name
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def test_get_current_user_authenticated(self):
        """Test getting current user data when authenticated"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(self.current_user_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["email"], "test@swsc.edu.np")

    def test_get_current_user_unauthenticated(self):
        """Test getting current user data when not authenticated"""
        response = self.client.get(self.current_user_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_current_user(self):
        """Test updating current user data"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        update_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane@mail.com",
        }
        response = self.client.patch(self.current_user_url, update_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["first_name"], "Jane")
        self.assertEqual(response.data["data"]["last_name"], "Smith")
        self.assertEqual(response.data["data"]["email"], "test@swsc.edu.np")

    def test_update_current_user_partial_data(self):
        """Test updating current user with partial data"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        update_data = {"first_name": "Jane"}
        response = self.client.patch(self.current_user_url, update_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["first_name"], "Jane")
        self.assertEqual(
            response.data["data"]["last_name"], "Doe"
        )  # Should remain unchanged


class ProfileViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            password="password123",
        )
        self.profile = self.user.profile
        self.profile.phone_number = "+9779840033004"
        self.profile.save()
        self.profile_url = reverse("current_user_profile")  # Add this URL name
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def test_get_profile_authenticated(self):
        """Test getting profile data when authenticated"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["phone_number"], "+9779840033004")
        self.assertFalse(response.data["data"]["is_phone_number_verified"])

    def test_get_profile_unauthenticated(self):
        """Test getting profile data when not authenticated"""
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile(self):
        """Test updating profile data"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        update_data = {"phone_number": "9840033004"}
        response = self.client.patch(self.profile_url, update_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["phone_number"], "+9779840033004")

    def test_update_profile_invalid_phone(self):
        """Test updating profile with invalid phone number"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        update_data = {"phone_number": "invalid-phone"}
        response = self.client.patch(self.profile_url, update_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
