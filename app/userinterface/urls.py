from django.urls import include, path
from rest_framework import routers
from userinterface import views
from django.views.generic import RedirectView
from django.conf.urls import url

urlpatterns= [
    path('main/', views.main, name='main'),
    url(r'^favicon\.ico$',RedirectView.as_view(url='/static/img/favicon.ico')),
]