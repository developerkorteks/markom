from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.change_password, name='change_password'),
    
    # User Management (Admin only)
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:pk>/toggle-active/', views.user_toggle_active, name='user_toggle_active'),
    
    # Bulk Import (Admin only)
    path('users/bulk-import/', views.bulk_import_users, name='bulk_import'),
    path('users/bulk-import/confirm/', views.bulk_import_confirm, name='bulk_import_confirm'),
    path('users/bulk-import/download/', views.bulk_import_download_result, name='bulk_import_download'),
]
