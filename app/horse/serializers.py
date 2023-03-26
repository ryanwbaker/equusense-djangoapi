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
    api_key = serializers.CharField(source='horse.api_key')
    horse_name = serializers.CharField(source='horse.name', read_only=True)

    class Meta:
        model = DataPoint
        fields = ['id', 'api_key', 'horse_name', 'hr', 'hr_interval','date_created', 'gps_lat', 'gps_long', 'temp', 'batt']
        read_only_fields = ['id', 'api_key', 'horse_name']

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

