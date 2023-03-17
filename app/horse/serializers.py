"""
Serializers for horse APIs.
"""
from rest_framework import serializers

from core.models import (
    Horse, 
    DataPoint
)


class HorseSerializer(serializers.ModelSerializer):
    """Serializer for horses."""

    class Meta:
        model = Horse
        fields = ['id', 'name', 'api_key', 'image']
        read_only_fields = ['id']

class DataPointSerializer(serializers.ModelSerializer):
    """Serializer for data points."""

    class Meta(HorseSerializer.Meta):
        model = DataPoint
        fields = HorseSerializer.Meta.fields + ['id', 'date_created', 'gps_lat', 'gps_long', 'temp', 'hr', 'hr_interval']
        read_only_fields = ['id']

class HorseDetailSerializer(HorseSerializer):
    """Serializer for horse detail view."""
    
    class Meta(HorseSerializer.Meta):
        # Add new detail fields here
        # eg. fields = HorseSerializer.Meta.fields + [new_field1, new_field2]
        fields = HorseSerializer.Meta.fields


class HorseImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to horses."""

    class Meta:
        model = Horse
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}

