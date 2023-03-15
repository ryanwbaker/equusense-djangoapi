"""
Tests for the data api
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from django.utils.crypto import get_random_string

from rest_framework import status
from rest_framework.test import APIClient

from core.models import DataPoint, Horse

from horse.serializers import DataPointSerializer


DATA_URL = reverse('horse:datapoint-list')
HORSES_URL = reverse('horse:horse-list')

def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)

def create_horse(user, **params):
    """Create and return a horse."""
    defaults = {
        'name': 'Sample Horse',
        'api_key': get_random_string(length=12),
    }
    defaults.update(params)

    horse = Horse.objects.create(user=user, **defaults)
    return horse

class PublicDataApiTests(TestCase):
    """Test unauthenticated API requests."""
    
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.horse1 = create_horse(self.user)
        self.horse2 = create_horse(self.user)
        DataPoint.objects.create(api_key=self.horse1, 
                                 gps_lat=37.428135, 
                                 gps_long=-122.079254, 
                                 temp=36.25, 
                                 hr=24.6,
                                 hr_interval=540)
        DataPoint.objects.create(api_key=self.horse2, 
                                gps_lat=36.428135, 
                                gps_long=100.079254, 
                                temp=34.10, 
                                hr=25.4,
                                hr_interval=600)
        self.client.force_authenticate(user=None)

    def test_auth_required_get(self):
        """Test auth is required for retrieving Data."""
        res = self.client.get(DATA_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_not_required_api_key_required_post(self):
        """Test auth is not required but an API key is required to make Data requests."""
        horse4 = create_horse(self.user)
        payload = {
            'gps_lat': 37.428135,
            'gps_long': -122.079254,
            'temp': 36.25,
            'hr': 24.6,
            'hr_interval': 540,
            'api_key': str(horse4.api_key),
        }
        res = self.client.post(DATA_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)




# class PrivateDataApiTests(TestCase):
#     """Test authenticated API requests."""
    
#     def setUp(self):
#         self.user = create_user()
#         self.horse1 = create_horse(self.user)
#         self.horse2 = create_horse(self.user, name="Sample Horse 2")
#         self.client = APIClient()
#         self.client.force_authenticate(self.user)

#     def test_retrieve_data(self):
#         """Test retrieving data for a given user."""
#         DataPoint.objects.create(api_key=self.horse1, 
#                                  gps_lat=37.428135, 
#                                  gps_long=-122.079254, 
#                                  temp=36.25, 
#                                  hr=24.6,
#                                  hr_interval=540)
#         DataPoint.objects.create(api_key=self.horse2, 
#                                 gps_lat=36.428135, 
#                                 gps_long=100.079254, 
#                                 temp=34.10, 
#                                 hr=25.4,
#                                 hr_interval=600)
        
#         res = self.client.get(DATA_URL)
#         # Specify order of return to be database agnostic
#         datapoints = DataPoint.objects.all().order_by('-api_key')
#         serializer = DataPointSerializer(datapoints, many=True)
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data, serializer.data)

#     def data_limited_to_user(self):
#         user2 = create_user(email='user2@example.com', password='pass123')
#         horse3 = create_horse(user2, name="Sample Horse 3")
#         DataPoint.objects.create(api_key=horse3,
#                                     gps_lat=37.428135, 
#                                     gps_long=-122.079254, 
#                                     temp=36.25, 
#                                     hr=24.6,
#                                     hr_interval=540)
        
#         datapoints = DataPoint.objects.create(api_key=self.horse2,
#                                             gps_lat=37.428135, 
#                                             gps_long=-122.079254, 
#                                             temp=36.25, 
#                                             hr=24.6,
#                                             hr_interval=540)
#         res = self.client.get(DATA_URL)
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(res.data), 1)
#         self.assertEqual(res.data[0], datapoints.id)




