from django.contrib import admin
from .models import Category, Merchandise, StockHistory

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Category"""
    list_display = ['name', 'is_active', 'merchandise_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Merchandise)
class MerchandiseAdmin(admin.ModelAdmin):
    """Admin interface for Merchandise"""
    list_display = ['name', 'category', 'stock', 'is_active', 'created_by', 'created_at']
    list_filter = ['is_active', 'category', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_by', 'created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(StockHistory)
class StockHistoryAdmin(admin.ModelAdmin):
    """Admin interface for StockHistory"""
    list_display = ['merchandise', 'adjustment', 'stock_before', 'stock_after', 'reason', 'adjusted_by', 'created_at']
    list_filter = ['created_at', 'adjusted_by']
    search_fields = ['merchandise__name', 'reason']
    readonly_fields = ['merchandise', 'adjustment', 'stock_before', 'stock_after', 'reason', 'adjusted_by', 'created_at']
    
    def has_add_permission(self, request):
        return False  # Prevent manual creation
    
    def has_change_permission(self, request, obj=None):
        return False  # Prevent editing
    
    def has_delete_permission(self, request, obj=None):
        return False  # Prevent deletion
