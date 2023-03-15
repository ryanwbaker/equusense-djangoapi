"""
Views for the horse APIs.
"""
from rest_framework import (
    viewsets,
    mixins,
    permissions,
)
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from .custom_authentication import CustomAuthentication
from .custom_permission import CustomPermission

from core.models import (
    Horse,
    DataPoint,
)
from horse import serializers

def get_horse_from_api_key(api_key):
    try:
        horse = Horse.objects.get(api_key=api_key)
        return horse
    except Horse.DoesNotExist:
        raise serializers.ValidationError('Invalid API key.')

class HorseViewSet(viewsets.ModelViewSet):
    """View for manage horse APIs."""
    serializer_class = serializers.HorseSerializer
    queryset = Horse.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve horses for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')
    
    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.HorseSerializer
        
        return self.serializer_class
    
    def perform_create(self, serializer):
        """Create a new horse."""
        serializer.save(user=self.request.user)

class DataPointViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Manage data points in the database"""
    serializer_class = serializers.DataPointSerializer
    queryset = DataPoint.objects.all()
    authentication_classes = [CustomAuthentication]
    permission_classes = [CustomPermission, IsAuthenticated]
        
    def get_queryset(self):
        """Filter queryset to authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')
    
    def perform_create(self, serializer):
        # Get the horse associated with the API key
        horse = get_horse_from_api_key(self.request.data['api_key'])

        # Populate the user field with the user of the horse
        serializer.save(user=horse.user, api_key=horse)

    def get_permissions(self):
        if self.action == 'create':
            return[AllowAny()]
        return [IsAuthenticated()]