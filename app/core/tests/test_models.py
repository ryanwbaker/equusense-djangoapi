"""
Tests for models.
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email='user@example.com', password='testpass123'):
    """"Create and return a new user."""
    return get_user_model().objects.create_user(email, password)

class ModelTests(TestCase):
    """Test models."""
    
    def test_create_user_with_email_successful(self):
        """Test if creating a user with an email is successful"""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password), password)
    
    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_horse(self):
        """Test creating a horse is successful."""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )
        horse = models.Horse.objects.create(
            user=user,
            name='Sample Horse Name'
        )

        self.assertEqual(str(horse), horse.name+" "+horse.api_key)

    def test_create_data_point(self):
        """Test creating a data point is successful."""
        self.user=create_user()
        self.horse=models.Horse.objects.create(
            user=self.user,
            name='Sample Horse Name'
        )
        test_data = {
            'gps_lat':40.866389,
            'gps_long':40.866389,
            'temp':-124.082778,
            'hr':31.8,
            'hr_interval':300.4,
        }
        data_point = models.DataPoint.objects.create(
            api_key=self.horse,
            gps_lat=test_data['gps_lat'],
            gps_long=test_data['gps_long'],
            temp=test_data['temp'],
            hr=test_data['hr'],
            hr_interval=test_data['hr_interval'],
        )
        self.assertEqual(data_point.api_key.api_key, self.horse.api_key)
        self.assertEqual(data_point.gps_lat, test_data['gps_lat'])
        self.assertEqual(data_point.gps_long, test_data['gps_long'])
        self.assertEqual(data_point.temp, test_data['temp'])
        self.assertEqual(data_point.hr, test_data['hr'])
        self.assertEqual(data_point.hr_interval, test_data['hr_interval'])
        self.assertEqual(data_point.user, self.horse.user)