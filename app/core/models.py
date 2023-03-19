"""
Database models.
"""
import uuid
import os

from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

def horse_image_file_path(instance, filename):
    """Generate file path for new horse image."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'horse', filename)

class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save, and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db )

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

def get_default_horse():
    return Horse.objects.first()

def get_default_user():
    return User.objects.first()

class Horse(models.Model):
    """Horse object."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    api_key = models.CharField(max_length=12, unique=True, default=get_random_string(length=12))
    image = models.ImageField(null=True, upload_to=horse_image_file_path)

    def __str__(self):
        return self.name+" "+self.api_key
    
class DataPoint(models.Model):
    """Data point for horse data."""
    horse = models.ForeignKey(Horse, 
                                on_delete=models.CASCADE, 
                                default=get_default_horse)
    @property
    def name(self):
        return self.horse.name
    
    @property
    def api_key(self):
        return self.horse.api_key
    
    @property
    def image(self):
        return self.horse.image

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        default=get_default_user)
    date_created = models.DateTimeField(auto_now_add=True)
    gps_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    gps_long = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    temp = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    hr = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    hr_interval = models.DecimalField(max_digits=7, decimal_places=2, null=True)

    def __str__(self):
        return self.api_key+" "+self.name+" "+str(self.date_created)


