"""Views for the User Interface"""
from django.shortcuts import render, redirect
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework import viewsets
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

def main(request):
    response = render(request, 'main.html')
    return response
