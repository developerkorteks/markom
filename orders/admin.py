from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    """Inline for order items"""
    model = OrderItem
    extra = 0
    readonly_fields = ['merchandise_name', 'quantity']
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for Order"""
    list_display = ['order_number', 'customer_name', 'customer_phone', 'sales_user', 'total_items', 'created_at']
    list_filter = ['created_at', 'sales_user']
    search_fields = ['order_number', 'customer_name', 'customer_phone']
    readonly_fields = ['order_number', 'created_at']
    inlines = [OrderItemInline]
    
    def has_add_permission(self, request):
        return False  # Prevent manual creation through admin
    
    def has_change_permission(self, request, obj=None):
        return False  # Prevent editing
    
    def has_delete_permission(self, request, obj=None):
        return False  # Prevent deletion

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin interface for OrderItem"""
    list_display = ['order', 'merchandise_name', 'quantity']
    list_filter = ['order__created_at']
    search_fields = ['order__order_number', 'merchandise_name']
    readonly_fields = ['order', 'merchandise', 'merchandise_name', 'quantity']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
