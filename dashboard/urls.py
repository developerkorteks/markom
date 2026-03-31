from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('api/produk/', views.admin_products_json, name='admin_products_json'),
]
