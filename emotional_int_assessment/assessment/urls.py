from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('assessment/', views.assessment, name='assessment'),
    path('result/', views.result, name='result'),
    # path('check/', views.check, name='check'),
]   