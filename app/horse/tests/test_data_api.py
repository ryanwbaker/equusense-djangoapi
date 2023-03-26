"""
Tests for the DataPoints API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from django.utils.crypto import get_random_string

from rest_framework import status
from rest_framework.test import APIClient
from datetime import datetime
from core.models import Horse, DataPoint

from horse.serializers import DataPointSerializer


DATAPOINT_URL = reverse('horse:datapoint-list')

sample_dps=[
    {'gps_lat': 123.456789,
     'gps_long': -123.456789,
     'temp': 36.4,
     'hr': 24.1,
     'hr_interval': 540,
     'batt': 55.4},
     {'gps_lat': 345.678901,
     'gps_long': -345.678901,
     'temp': 37.4,
     'hr': 19.9,
     'hr_interval': 360,
     'batt': 25.3},
     {'gps_lat': 456.789012,
     'gps_long': -456.789012,
     'temp': 24.5,
     'hr': 36.2,
     'hr_interval': 480,
     'batt': 29.4},
     {'gps_lat': 567.890123,
     'gps_long': -567.890123,
     'temp': 33.2,
     'hr': 25.6,
     'hr_interval': 300, 
     'batt': 25.3}
]

def detail_url(datapoint_id):
    """Create and return a datapoint url."""
    return reverse('horse:datapoint-detail', args=[datapoint_id])

def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)

def create_horse(user, name='Sample Horse'):
    return Horse.objects.create(user=user, name=name, api_key=get_random_string(length=12))

def create_dp(user, horse, data_dict):
    return DataPoint.objects.create(user=user, horse=horse, **data_dict)

class PublicDataPointApiTests(TestCase):
    """Test unauthenticated API requests."""
    
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving data points."""
        res = self.client.get(DATAPOINT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateDataPointApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_datapoints(self):
        """Test retrieving a list of datapoints."""
        horse = create_horse(self.user, "Sample horse 1")
        create_dp(self.user, horse, sample_dps[0])
        create_dp(self.user, horse, sample_dps[1])
        res = self.client.get(DATAPOINT_URL)
        datapoints = DataPoint.objects.all().order_by('-id')
        serializer = DataPointSerializer(datapoints, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_datapoints_limited_to_user(self):
        """Test list of datapoints limited to authenticated user."""
        horse1 = create_horse(self.user, "Sample Horse 1")
        dp_data = [sample_dps[0], sample_dps[1]]
        dps = []
        for dp in dp_data:
            dps.append(create_dp(self.user, horse1, dp))
        # Note that view returns data in descending ID order
        # First datapoint in list will be the last one created
        # reverse the list so API return matches list
        dp_data.reverse()
        user2 = create_user(email="user2@example.com")
        horse2 = create_horse(user=user2, name="test horse 2")
        create_dp(user2, horse2, sample_dps[1])
        res = self.client.get(DATAPOINT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data[0]['api_key'], horse1.api_key)
        for i, dp in enumerate(dp_data):
            res_dict = dict(res.data[i])
            for key, value in dp.items():
                self.assertEqual(float(res_dict[key]), float(value))

    def test_update_datapoint(self):
        """Test updating a datapoint."""
        payload={**sample_dps[1]}
        horse1 = create_horse(self.user, "Sample Horse 1")
        dp1 = create_dp(self.user, horse1, sample_dps[0])
        url = detail_url(dp1.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        dp1.refresh_from_db()
        for key, value in sample_dps[1].items():
            self.assertEqual(getattr(dp1, key).__float__(), float(value))

    def test_delete_datapoint(self):
        """Test deleting a datapoint."""
        horse1 = create_horse(self.user, "Sample Horse 1")
        dp = create_dp(self.user, horse1, sample_dps[0])
        url = detail_url(dp.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        dps = DataPoint.objects.filter(user=self.user)
        self.assertFalse(dps.exists())

    def test_create_datapoint(self):
        """Test creating a datapoint."""
        horse1 = create_horse(self.user, "Sample Horse 1")
        payload = {'api_key': horse1.api_key, **sample_dps[0]}
        res = self.client.post(DATAPOINT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        res_data = dict(res.data)
        for key, value in payload.items():
            if type(value) is str:
                self.assertEqual(res_data[key], value)
            else:
                self.assertEqual(float(res_data[key]), value)
    
    def test_filter_by_date_and_api_key(self):
        """Test filtering datapoints by horse and date."""
        horse1 = create_horse(self.user, "Sample Horse 1")
        dp_data = [sample_dps[0], sample_dps[1], sample_dps[2], sample_dps[3]]
        dps = []
        for dp in dp_data:
            dps.append(create_dp(self.user, horse1, dp))

        dates = ["2023-03-17T23:59:59.000", 
                 "2023-03-18T23:59:59.000", 
                 "2023-03-19T23:59:59.000", 
                 "2023-03-20T23:59:59.000"]
        for i, dp in enumerate(dps):
            dp.date_created = datetime.fromisoformat(dates[i])
            dp.save()
        horse2 = create_horse(user=self.user, name="BAD BAD HORSE")
        create_dp(self.user, horse2, sample_dps[0])

        params = {
            'horse__api_key': horse1.api_key,
            'date_created__gt': '2023-03-19',
        }
        
        res = self.client.get(DATAPOINT_URL, params)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

        for dp in res.data:
            self.assertEqual(dp['api_key'], horse1.api_key)

