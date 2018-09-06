from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('unsubscribe/', views.unsubscribe, name='unsubscribe'),
    path('status/', views.status, name='status'),
]
