from django.urls import path
from . import views
from . import cart_views

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

    # Cart URLs
    path('keranjang/', cart_views.cart_detail, name='cart_detail'),
    path('keranjang/tambah/<int:merchandise_id>/', cart_views.cart_add, name='cart_add'),
    path('keranjang/update/<int:merchandise_id>/', cart_views.cart_update, name='cart_update'),
    path('keranjang/hapus/<int:merchandise_id>/', cart_views.cart_remove, name='cart_remove'),
    path('keranjang/kosongkan/', cart_views.cart_clear, name='cart_clear'),

    # Shop & Checkout URLs
    path('katalog/', cart_views.shop, name='shop'),
    path('katalog/<int:merchandise_id>/', cart_views.shop_detail, name='shop_detail'),
    path('checkout/', cart_views.checkout, name='checkout'),

    # Sales order history (card-based)
    path('riwayat/', cart_views.my_orders, name='my_orders'),

    # AJAX: products JSON untuk pagination di dashboard
    path('api/produk/', cart_views.products_json, name='products_json'),
]
