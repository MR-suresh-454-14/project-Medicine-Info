from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tablet/<str:name>/', views.tablet_detail, name='tablet_detail'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
]
