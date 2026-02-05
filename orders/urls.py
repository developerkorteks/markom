from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Order URLs
    path('create/', views.order_create, name='order_create'),
    path('', views.order_list, name='order_list'),
    path('<int:pk>/', views.order_detail, name='order_detail'),
    path('<int:pk>/print/', views.order_print, name='order_print'),
    
    # Export URLs
    path('export/excel/', views.order_export_excel, name='order_export_excel'),
    path('<int:pk>/export/excel/', views.order_export_detail_excel, name='order_export_detail_excel'),
    
    # AJAX endpoints
    path('ajax/stock-check/', views.merchandise_stock_check, name='stock_check'),
]
