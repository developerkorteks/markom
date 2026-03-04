from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Admin views
    path('', views.inventory_list, name='inventory_list'),
    path('<int:user_pk>/', views.inventory_detail, name='inventory_detail'),
    path('<int:user_pk>/allocate/', views.inventory_allocate, name='inventory_allocate'),
    # Sales views
    path('my/', views.my_inventory, name='my_inventory'),
    path('my/checkout/', views.my_inventory_checkout, name='my_inventory_checkout'),
]
