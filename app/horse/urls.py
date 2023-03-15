"""
URL mappings for the horse app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from horse import views


router = DefaultRouter()
router.register('horses', views.HorseViewSet)
router.register('datapoints', views.DataPointViewSet)

app_name = 'horse'

urlpatterns = [
    path('', include(router.urls))
]