from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), # if user login run this line render home.html
    path('tablet/<str:name>/', views.tablet_detail, name='tablet_detail'), # after user typing the tablet name and click search go to the tablet_detail.html
    path('autocomplete/', views.autocomplete, name='autocomplete'),
]
