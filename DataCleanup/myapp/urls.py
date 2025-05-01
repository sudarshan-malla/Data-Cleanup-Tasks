from django.shortcuts import render
from django.urls import path
from . import views

urlpatterns = [
    path('', lambda r: render(r, 'index.html')),
    path('upload', views.upload_dataset),
    path('run_task/<str:task>', views.run_task),
]
