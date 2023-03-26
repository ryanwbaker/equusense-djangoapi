"""
Views for the horse APIs.
"""
from rest_framework import (
    viewsets,
    mixins,
    status,
    filters,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import (
    DjangoFilterBackend,
    DateFromToRangeFilter
)

from core.models import (
    Horse,
    DataPoint,
)

from horse import serializers
from horse.filters import DataPointFilter

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
        elif self.action == 'upload_image':
            return serializers.HorseImageSerializer
        
        return self.serializer_class
    
    def perform_create(self, serializer):
        """Create a new horse."""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        horse = self.get_object()
        serializer = self.get_serializer(horse, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DataPointViewSet(mixins.CreateModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.ListModelMixin, 
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    """Manage data points in the database"""
    serializer_class = serializers.DataPointSerializer
    queryset = DataPoint.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = DataPointFilter
        
    def get_queryset(self):
        """Filter queryset to authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')
    
    def perform_create(self, serializer):
        # Get the horse associated with the API key
        horse = get_horse_from_api_key(self.request.data['api_key'])

        # Populate the user field with the user of the horse
        serializer.save(user=self.request.user, horse=horse)
