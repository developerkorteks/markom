from django.urls import path
from . import views

app_name = 'merchandise'

urlpatterns = [
    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('categories/<int:pk>/toggle-active/', views.category_toggle_active, name='category_toggle_active'),
    
    # Merchandise URLs
    path('', views.merchandise_list, name='merchandise_list'),
    path('create/', views.merchandise_create, name='merchandise_create'),
    path('<int:pk>/', views.merchandise_detail, name='merchandise_detail'),
    path('<int:pk>/edit/', views.merchandise_edit, name='merchandise_edit'),
    path('<int:pk>/delete/', views.merchandise_delete, name='merchandise_delete'),
    path('<int:pk>/toggle-active/', views.merchandise_toggle_active, name='merchandise_toggle_active'),
    path('<int:pk>/adjust-stock/', views.merchandise_adjust_stock, name='merchandise_adjust_stock'),
]
