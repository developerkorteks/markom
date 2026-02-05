from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Count, Sum
from django.http import JsonResponse
from accounts.decorators import admin_required, admin_or_sales_required
from .models import Order, OrderItem
from .forms import OrderForm, OrderItemFormSet
from .utils import export_orders_to_excel, export_order_details_to_excel
from merchandise.models import Merchandise

@admin_or_sales_required
def order_create(request):
    """Create new order (Admin & Sales)"""
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        item_formset = OrderItemFormSet(request.POST)
        
        if order_form.is_valid() and item_formset.is_valid():
            try:
                with transaction.atomic():
                    # Create order
                    order = order_form.save(commit=False)
                    order.sales_user = request.user
                    order.save()
                    
                    # Create order items
                    items_created = 0
                    for item_form in item_formset:
                        if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                            merchandise = item_form.cleaned_data['merchandise']
                            quantity = item_form.cleaned_data['quantity']
                            
                            OrderItem.objects.create(
                                order=order,
                                merchandise=merchandise,
                                quantity=quantity
                            )
                            items_created += 1
                    
                    messages.success(
                        request,
                        f'Order {order.order_number} created successfully with {items_created} item(s)!'
                    )
                    return redirect('orders:order_detail', pk=order.pk)
                    
            except Exception as e:
                messages.error(request, f'Error creating order: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        order_form = OrderForm()
        item_formset = OrderItemFormSet()
    
    # Get available merchandise for selection
    available_merchandise = Merchandise.objects.filter(
        is_active=True,
        stock__gt=0
    ).select_related('category').order_by('category__name', 'name')
    
    context = {
        'order_form': order_form,
        'item_formset': item_formset,
        'available_merchandise': available_merchandise
    }
    
    return render(request, 'orders/order_create.html', context)

@admin_or_sales_required
def order_list(request):
    """List orders (Admin: all, Sales: own)"""
    search_query = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Base queryset
    if request.user.is_admin:
        orders = Order.objects.select_related('sales_user').all()
        title = 'All Orders'
    else:
        orders = Order.objects.filter(sales_user=request.user).all()
        title = 'My Orders'
    
    # Apply search filter
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(customer_name__icontains=search_query) |
            Q(customer_phone__icontains=search_query)
        )
    
    # Apply date filters
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)
    
    # Annotate with item counts
    orders = orders.annotate(
        item_count=Count('items'),
        total_quantity=Sum('items__quantity')
    )
    
    context = {
        'orders': orders,
        'title': title,
        'search_query': search_query,
        'date_from': date_from,
        'date_to': date_to
    }
    
    return render(request, 'orders/order_list.html', context)

@admin_or_sales_required
def order_detail(request, pk):
    """View order details (Admin: all, Sales: own)"""
    order = get_object_or_404(
        Order.objects.select_related('sales_user').prefetch_related('items__merchandise'),
        pk=pk
    )
    
    # Check permission (sales can only view own orders)
    if request.user.is_sales and order.sales_user != request.user:
        messages.error(request, 'You can only view your own orders.')
        return redirect('orders:order_list')
    
    context = {
        'order': order
    }
    
    return render(request, 'orders/order_detail.html', context)

@admin_or_sales_required
def order_print(request, pk):
    """Print order form (Admin: all, Sales: own)"""
    order = get_object_or_404(
        Order.objects.select_related('sales_user').prefetch_related('items__merchandise'),
        pk=pk
    )
    
    # Check permission (sales can only print own orders)
    if request.user.is_sales and order.sales_user != request.user:
        messages.error(request, 'You can only print your own orders.')
        return redirect('orders:order_list')
    
    context = {
        'order': order
    }
    
    return render(request, 'orders/order_print.html', context)

@admin_or_sales_required
def merchandise_stock_check(request):
    """AJAX endpoint to check merchandise stock"""
    merchandise_id = request.GET.get('merchandise_id')
    
    if not merchandise_id:
        return JsonResponse({'error': 'Merchandise ID required'}, status=400)
    
    try:
        merchandise = Merchandise.objects.get(pk=merchandise_id, is_active=True)
        return JsonResponse({
            'stock': merchandise.stock,
            'name': merchandise.name,
            'is_low_stock': merchandise.is_low_stock,
            'is_out_of_stock': merchandise.is_out_of_stock
        })
    except Merchandise.DoesNotExist:
        return JsonResponse({'error': 'Merchandise not found'}, status=404)

@admin_or_sales_required
def order_export_excel(request):
    """Export orders to Excel with filters"""
    search_query = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Base queryset
    if request.user.is_admin:
        orders = Order.objects.select_related('sales_user').all()
    else:
        orders = Order.objects.filter(sales_user=request.user).all()
    
    # Apply search filter
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(customer_name__icontains=search_query) |
            Q(customer_phone__icontains=search_query)
        )
    
    # Apply date filters
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)
    
    # Annotate with item counts
    orders = orders.annotate(
        item_count=Count('items'),
        total_quantity=Sum('items__quantity')
    )
    
    # Order by created date (newest first)
    orders = orders.order_by('-created_at')
    
    # Export to Excel
    return export_orders_to_excel(orders, user=request.user)

@admin_or_sales_required
def order_export_detail_excel(request, pk):
    """Export single order details to Excel"""
    order = get_object_or_404(
        Order.objects.select_related('sales_user').prefetch_related('items__merchandise__category'),
        pk=pk
    )
    
    # Check permission (sales can only export own orders)
    if request.user.is_sales and order.sales_user != request.user:
        messages.error(request, 'You can only export your own orders.')
        return redirect('orders:order_list')
    
    return export_order_details_to_excel(order)
