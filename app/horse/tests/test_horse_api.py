"""
Test for horse APIs.
"""
from decimal import Decimal
import tempfile
import os

from PIL import Image

from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Horse

from horse.serializers import (
    HorseSerializer,
    HorseDetailSerializer,
)


HORSES_URL = reverse('horse:horse-list')

def detail_url(horse_id):
    """Create and return a horse detail URL."""
    return reverse('horse:horse-detail', args=[horse_id])


def image_upload_url(horse_id):
    """Create and return an image upload URL."""
    return reverse('horse:horse-upload-image', args=[horse_id])


def create_horse(user, **params):
    """Create and return a horse."""
    defaults = {
        'name': 'Sample Horse',
        'api_key': get_random_string(length=12),
    }
    defaults.update(params)

    horse = Horse.objects.create(user=user, **defaults)
    return horse


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicHorseAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(HORSES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateHorseAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com',password='testpass123')
        self.client.force_authenticate(self.user)

    def test_retrieve_horses(self):
        """Test retrieving a list of horses."""
        create_horse(user=self.user)
        create_horse(user=self.user)

        res = self.client.get(HORSES_URL)
        horses = Horse.objects.all().order_by('-id')
        serializer = HorseSerializer(horses, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_horse_list_limited_to_user(self):
        """Test list of horses is limited to authenticated user."""
        other_user = create_user(email='other@example.com',password='password234')
        create_horse(user=other_user)
        create_horse(user=self.user)

        res = self.client.get(HORSES_URL)

        horses = Horse.objects.filter(user=self.user)
        serializer = HorseSerializer(horses, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_horse_detail(self):
        """Test get horse detail."""
        horse = create_horse(user=self.user)

        url = detail_url(horse.id)
        res = self.client.get(url)

        serializer = HorseDetailSerializer(horse)
        self.assertEqual(res.data, serializer.data)

    def test_create_horse(self):
        """Test creating a horse."""
        payload = {
            'name': 'Sample Horse',
        }
        res = self.client.post(HORSES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        horse = Horse.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(horse, k), v)
        self.assertEqual(horse.user, self.user)


    def test_partial_update(self):
        """Test partial update of a horse."""
        horse = create_horse(
            user=self.user,
            name='Old Horse Name'
        )
        api_key = horse.api_key
        payload = {'name': 'New Horse Name'}
        url = detail_url(horse.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        horse.refresh_from_db()
        self.assertEqual(horse.name, payload['name'])
        self.assertEqual(horse.api_key, api_key)
        self.assertEqual(horse.user, self.user)
    
    def test_full_update(self):
        """Test full update of horse."""
        horse = create_horse(
            user = self.user,
            name = 'Old Horse Name',
        )

        payload = {'name': 'New Horse Name'}
        url = detail_url(horse.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        horse.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(horse, k), v)
        self.assertEqual(horse.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the horse user returns an error."""
        new_user = create_user(email='user2@example.com', password='test456')
        horse = create_horse(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(horse.id)
        self.client.patch(url, payload)
        
        horse.refresh_from_db()
        self.assertEqual(horse.user, self.user)

    def test_delete_horse(self):
        """Test deleting a horse is successful."""
        horse = create_horse(user=self.user)

        url = detail_url(horse.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Horse.objects.filter(id=horse.id).exists())

    def test_delete_other_users_horse_error(self):
        """Test trying to delete another user's horse gives error."""
        new_user = create_user(email='user2@example.com', password='test789')
        horse = create_horse(user=new_user)

        url = detail_url(horse.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Horse.objects.filter(id=horse.id).exists())



class ImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'password123'
        )
        self.client.force_authenticate(self.user)
        self.horse = create_horse(user=self.user)

    def tearDown(self) -> None:
        self.horse.image.delete()

    def test_upload_image(self):
        """Test uploading an image to a horse."""
        url = image_upload_url(self.horse.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10,10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')
        
        self.horse.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.horse.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading invalid image."""
        url = image_upload_url(self.horse.id)
        payload = {'image':'notanimage'}
        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

