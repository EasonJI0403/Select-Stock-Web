from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('data/', views.get_data, name='get_data'),
    path('select-stock/', views.select_stock_view, name='select_stock'),
]