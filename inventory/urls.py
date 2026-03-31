from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Admin - Category Management
    path('tools/categories/', views.tool_category_list, name='tool_category_list'),
    path('tools/categories/create/', views.tool_category_create, name='tool_category_create'),
    path('tools/categories/<int:pk>/edit/', views.tool_category_update, name='tool_category_update'),
    path('tools/categories/<int:pk>/delete/', views.tool_category_delete, name='tool_category_delete'),

    # Admin - Tools Management
    path('tools/', views.tool_list, name='tool_list'),
    path('tools/create/', views.tool_create, name='tool_create'),
    path('tools/<int:pk>/edit/', views.tool_update, name='tool_update'),
    path('tools/<int:pk>/delete/', views.tool_delete, name='tool_delete'),
    path('tools/<int:pk>/adjust-stock/', views.tool_adjust_stock, name='tool_adjust_stock'),

    # Sales - Tools Catalog & Checkout
    path('catalog/', views.tools_catalog, name='tools_catalog'),
    path('checkout/', views.tool_checkout, name='tool_checkout'),
    path('checkout/<int:pk>/', views.tool_checkout, name='tool_checkout_pk'),
    path('my-checkouts/', views.my_checkouts, name='my_checkouts'),
    path('my-checkouts/<int:pk>/', views.checkout_detail, name='checkout_detail'),

    # Admin - Review Checkouts
    path('review/', views.checkout_review_list, name='checkout_review_list'),
    path('review/<int:pk>/', views.checkout_review, name='checkout_review'),

    # Legacy redirects
    path('', views.inventory_list, name='inventory_list'),
    path('<int:user_pk>/', views.inventory_detail, name='inventory_detail'),
    path('<int:user_pk>/allocate/', views.inventory_allocate, name='inventory_allocate'),
    path('my/', views.my_inventory, name='my_inventory'),
    path('my/checkout/', views.my_inventory_checkout, name='my_inventory_checkout'),
]
