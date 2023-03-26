import django_filters
from core.models import DataPoint

class DataPointFilter(django_filters.FilterSet):
    horse__api_key = django_filters.CharFilter(field_name='horse__api_key')
    date_created__gte = django_filters.DateTimeFilter(field_name='date_created', lookup_expr='gte')
    date_created__lte = django_filters.DateTimeFilter(field_name='date_created', lookup_expr='lte')
    date_created__lt = django_filters.DateTimeFilter(field_name='date_created', lookup_expr='lt')
    date_created__gt = django_filters.DateTimeFilter(field_name='date_created', lookup_expr='gt')

    class Meta:
        model = DataPoint
        fields = [
            'horse__api_key', 
            'date_created__lt',
            'date_created__lte',
            'date_created__gt',
            'date_created__gte',
            ]