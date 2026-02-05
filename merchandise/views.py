from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from accounts.decorators import admin_required, admin_or_sales_required
from .models import Category, Merchandise, StockHistory
from .forms import CategoryForm, MerchandiseForm, StockAdjustmentForm

# ============================================
# CATEGORY VIEWS
# ============================================

@admin_required
def category_list(request):
    """List all categories (Admin only)"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    categories = Category.objects.all()
    
    # Apply search filter
    if search_query:
        categories = categories.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Apply status filter
    if status_filter == 'active':
        categories = categories.filter(is_active=True)
    elif status_filter == 'inactive':
        categories = categories.filter(is_active=False)
    
    context = {
        'categories': categories,
        'search_query': search_query,
        'status_filter': status_filter
    }
    
    return render(request, 'merchandise/category_list.html', context)

@admin_required
def category_create(request):
    """Create new category (Admin only)"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            try:
                category = form.save()
                messages.success(request, f'Category "{category.name}" created successfully.')
                return redirect('merchandise:category_list')
            except Exception as e:
                messages.error(request, f'Error creating category: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CategoryForm()
    
    return render(request, 'merchandise/category_form.html', {
        'form': form,
        'title': 'Create New Category',
        'button_text': 'Create Category'
    })

@admin_required
def category_edit(request, pk):
    """Edit existing category (Admin only)"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            try:
                category = form.save()
                messages.success(request, f'Category "{category.name}" updated successfully.')
                return redirect('merchandise:category_list')
            except Exception as e:
                messages.error(request, f'Error updating category: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'merchandise/category_form.html', {
        'form': form,
        'category': category,
        'title': f'Edit Category: {category.name}',
        'button_text': 'Update Category'
    })

@admin_required
def category_delete(request, pk):
    """Delete category (Admin only) - Soft delete"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        category_name = category.name
        try:
            # Check if has merchandise
            if category.merchandise_set.exists():
                messages.error(
                    request,
                    f'Cannot delete category "{category_name}" because it has merchandise. '
                    'Please move or delete merchandise first.'
                )
            else:
                category.delete()  # Soft delete
                messages.success(request, f'Category "{category_name}" deleted successfully.')
            return redirect('merchandise:category_list')
        except Exception as e:
            messages.error(request, f'Error deleting category: {str(e)}')
            return redirect('merchandise:category_list')
    
    return render(request, 'merchandise/category_confirm_delete.html', {
        'category': category,
        'merchandise_count': category.merchandise_count
    })

@admin_required
def category_toggle_active(request, pk):
    """Toggle category active status (Admin only)"""
    category = get_object_or_404(Category, pk=pk)
    
    category.is_active = not category.is_active
    category.save()
    
    status = 'activated' if category.is_active else 'deactivated'
    messages.success(request, f'Category "{category.name}" has been {status}.')
    
    return redirect('merchandise:category_list')

# ============================================
# MERCHANDISE VIEWS
# ============================================

@admin_or_sales_required
def merchandise_list(request):
    """List all merchandise (Admin: full access, Sales: view only active items)"""
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')
    stock_filter = request.GET.get('stock', '')
    
    # Filter based on role
    if request.user.is_admin:
        merchandise = Merchandise.objects.select_related('category', 'created_by').all()
    else:
        # Sales can only see active merchandise with stock
        merchandise = Merchandise.objects.select_related('category', 'created_by').filter(
            is_active=True
        )
    
    # Apply search filter
    if search_query:
        merchandise = merchandise.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Apply category filter
    if category_filter:
        merchandise = merchandise.filter(category_id=category_filter)
    
    # Apply status filter
    if status_filter == 'active':
        merchandise = merchandise.filter(is_active=True)
    elif status_filter == 'inactive':
        merchandise = merchandise.filter(is_active=False)
    
    # Apply stock filter
    if stock_filter == 'low':
        merchandise = merchandise.filter(stock__lt=10, stock__gt=0)
    elif stock_filter == 'out':
        merchandise = merchandise.filter(stock=0)
    
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'merchandise': merchandise,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
        'status_filter': status_filter,
        'stock_filter': stock_filter
    }
    
    return render(request, 'merchandise/merchandise_list.html', context)

@admin_required
def merchandise_create(request):
    """Create new merchandise (Admin only)"""
    if request.method == 'POST':
        form = MerchandiseForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                merchandise = form.save(commit=False)
                merchandise.created_by = request.user
                merchandise.save()
                messages.success(request, f'Merchandise "{merchandise.name}" created successfully.')
                return redirect('merchandise:merchandise_list')
            except Exception as e:
                messages.error(request, f'Error creating merchandise: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MerchandiseForm()
    
    return render(request, 'merchandise/merchandise_form.html', {
        'form': form,
        'title': 'Create New Merchandise',
        'button_text': 'Create Merchandise'
    })

@admin_required
def merchandise_edit(request, pk):
    """Edit existing merchandise (Admin only)"""
    merchandise = get_object_or_404(Merchandise, pk=pk)
    
    if request.method == 'POST':
        form = MerchandiseForm(request.POST, request.FILES, instance=merchandise)
        if form.is_valid():
            try:
                merchandise = form.save()
                messages.success(request, f'Merchandise "{merchandise.name}" updated successfully.')
                return redirect('merchandise:merchandise_list')
            except Exception as e:
                messages.error(request, f'Error updating merchandise: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MerchandiseForm(instance=merchandise)
    
    return render(request, 'merchandise/merchandise_form.html', {
        'form': form,
        'merchandise': merchandise,
        'title': f'Edit Merchandise: {merchandise.name}',
        'button_text': 'Update Merchandise'
    })

@admin_or_sales_required
def merchandise_detail(request, pk):
    """View merchandise details (Admin: full, Sales: view only)"""
    merchandise = get_object_or_404(
        Merchandise.objects.select_related('category', 'created_by'),
        pk=pk
    )
    stock_history = merchandise.stock_history.select_related('adjusted_by').all()[:10]
    
    context = {
        'merchandise': merchandise,
        'stock_history': stock_history
    }
    
    return render(request, 'merchandise/merchandise_detail.html', context)

@admin_required
def merchandise_delete(request, pk):
    """Delete merchandise (Admin only) - Soft delete"""
    merchandise = get_object_or_404(Merchandise, pk=pk)
    
    if request.method == 'POST':
        merchandise_name = merchandise.name
        try:
            merchandise.delete()  # Soft delete
            messages.success(request, f'Merchandise "{merchandise_name}" deleted successfully.')
            return redirect('merchandise:merchandise_list')
        except Exception as e:
            messages.error(request, f'Error deleting merchandise: {str(e)}')
            return redirect('merchandise:merchandise_list')
    
    return render(request, 'merchandise/merchandise_confirm_delete.html', {
        'merchandise': merchandise
    })

@admin_required
def merchandise_toggle_active(request, pk):
    """Toggle merchandise active status (Admin only)"""
    merchandise = get_object_or_404(Merchandise, pk=pk)
    
    merchandise.is_active = not merchandise.is_active
    merchandise.save()
    
    status = 'activated' if merchandise.is_active else 'deactivated'
    messages.success(request, f'Merchandise "{merchandise.name}" has been {status}.')
    
    return redirect('merchandise:merchandise_list')

@admin_required
def merchandise_adjust_stock(request, pk):
    """Adjust merchandise stock (Admin only)"""
    merchandise = get_object_or_404(Merchandise, pk=pk)
    
    if request.method == 'POST':
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            try:
                adjustment = form.cleaned_data['adjustment']
                reason = form.cleaned_data['reason']
                
                # Create stock adjustment
                StockHistory.create_adjustment(
                    merchandise=merchandise,
                    adjustment=adjustment,
                    reason=reason,
                    adjusted_by=request.user
                )
                
                sign = '+' if adjustment >= 0 else ''
                messages.success(
                    request,
                    f'Stock adjusted: {sign}{adjustment}. New stock: {merchandise.stock}'
                )
                return redirect('merchandise:merchandise_detail', pk=pk)
            except Exception as e:
                messages.error(request, f'Error adjusting stock: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StockAdjustmentForm()
    
    return render(request, 'merchandise/stock_adjust.html', {
        'form': form,
        'merchandise': merchandise
    })
