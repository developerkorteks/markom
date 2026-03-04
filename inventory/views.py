from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Q, Count
from django.contrib.auth import get_user_model
from accounts.decorators import admin_required, sales_required
from .sales_tool_models import SalesTool, ToolCheckout
from .tool_forms import SalesToolForm, ToolStockAdjustmentForm, ToolCheckoutForm, CheckoutReviewForm
from datetime import datetime, timedelta
from django.utils import timezone

User = get_user_model()

# ============================================
# ADMIN VIEWS - Tools Management
# ============================================

@admin_required
def tool_list(request):
    """Admin: List all sales tools"""
    search = request.GET.get('search', '')
    
    tools = SalesTool.objects.all().select_related('created_by').order_by('name')
    
    if search:
        tools = tools.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    
    return render(request, 'inventory/tool_list.html', {
        'tools': tools,
        'search': search,
        'title': 'Sales Tools Management'
    })


@admin_required
def tool_create(request):
    """Admin: Create new tool"""
    if request.method == 'POST':
        form = SalesToolForm(request.POST, request.FILES)
        if form.is_valid():
            tool = form.save(commit=False)
            tool.created_by = request.user
            tool.save()
            messages.success(request, f'Tool "{tool.name}" berhasil dibuat.')
            return redirect('inventory:tool_list')
        else:
            messages.error(request, 'Form tidak valid. Silakan periksa input Anda.')
    else:
        form = SalesToolForm()
    
    return render(request, 'inventory/tool_form.html', {
        'form': form,
        'title': 'Tambah Tool Baru',
        'action': 'create'
    })


@admin_required
def tool_update(request, pk):
    """Admin: Update tool"""
    tool = get_object_or_404(SalesTool, pk=pk)
    
    if request.method == 'POST':
        form = SalesToolForm(request.POST, request.FILES, instance=tool)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tool "{tool.name}" berhasil diupdate.')
            return redirect('inventory:tool_list')
        else:
            messages.error(request, 'Form tidak valid.')
    else:
        form = SalesToolForm(instance=tool)
    
    return render(request, 'inventory/tool_form.html', {
        'form': form,
        'tool': tool,
        'title': f'Edit Tool - {tool.name}',
        'action': 'update'
    })


@admin_required
def tool_delete(request, pk):
    """Admin: Delete tool (soft delete by setting is_active=False)"""
    tool = get_object_or_404(SalesTool, pk=pk)
    
    if request.method == 'POST':
        tool.is_active = False
        tool.save()
        messages.success(request, f'Tool "{tool.name}" telah dinonaktifkan.')
        return redirect('inventory:tool_list')
    
    return render(request, 'inventory/tool_confirm_delete.html', {
        'tool': tool,
        'title': f'Hapus Tool - {tool.name}'
    })


@admin_required
def tool_adjust_stock(request, pk):
    """Admin: Adjust tool stock"""
    tool = get_object_or_404(SalesTool, pk=pk)
    
    if request.method == 'POST':
        form = ToolStockAdjustmentForm(request.POST)
        if form.is_valid():
            adjustment = form.cleaned_data['adjustment']
            reason = form.cleaned_data['reason']
            
            try:
                with transaction.atomic():
                    if adjustment > 0:
                        tool.add_stock(adjustment)
                        action = 'ditambah'
                    else:
                        tool.deduct_stock(abs(adjustment))
                        action = 'dikurangi'
                    
                    messages.success(
                        request,
                        f'Stock "{tool.name}" berhasil {action} {abs(adjustment)} unit. Stock sekarang: {tool.stock}'
                    )
                return redirect('inventory:tool_list')
            except ValidationError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, 'Form tidak valid.')
    else:
        form = ToolStockAdjustmentForm()
    
    return render(request, 'inventory/tool_adjust_stock.html', {
        'form': form,
        'tool': tool,
        'title': f'Adjust Stock - {tool.name}'
    })


# ============================================
# SALES VIEWS - Tools Catalog & Checkout
# ============================================

@sales_required
def tools_catalog(request):
    """Sales: Browse available tools"""
    search = request.GET.get('search', '')
    
    tools = SalesTool.objects.filter(is_active=True).order_by('name')
    
    if search:
        tools = tools.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    
    return render(request, 'inventory/tools_catalog.html', {
        'tools': tools,
        'search': search,
        'title': 'Tools Catalog'
    })


@sales_required
def tool_checkout(request, pk=None):
    """Sales: Checkout a tool"""
    if request.method == 'POST':
        form = ToolCheckoutForm(request.POST)
        if form.is_valid():
            checkout = form.save(commit=False)
            checkout.sales_user = request.user
            checkout.save()
            
            messages.success(
                request,
                f'Checkout {checkout.quantity} unit "{checkout.tool.name}" berhasil. Menunggu persetujuan admin.'
            )
            return redirect('inventory:my_checkouts')
        else:
            messages.error(request, 'Form tidak valid.')
    else:
        # Pre-select tool if pk provided
        initial = {}
        if pk:
            tool = get_object_or_404(SalesTool, pk=pk, is_active=True)
            initial['tool'] = tool
        
        form = ToolCheckoutForm(initial=initial)
    
    return render(request, 'inventory/tool_checkout.html', {
        'form': form,
        'title': 'Checkout Tool'
    })


@sales_required
def my_checkouts(request):
    """Sales: View their checkout requests"""
    checkouts = ToolCheckout.objects.filter(
        sales_user=request.user
    ).select_related('tool', 'reviewed_by').order_by('-created_at')
    
    # Separate by status
    pending = checkouts.filter(status='PENDING')
    approved = checkouts.filter(status='APPROVED')
    rejected = checkouts.filter(status='REJECTED')
    
    return render(request, 'inventory/my_checkouts.html', {
        'pending': pending,
        'approved': approved,
        'rejected': rejected,
        'title': 'My Checkouts'
    })


# ============================================
# ADMIN VIEWS - Review Checkouts with Filters
# ============================================

@admin_required
def checkout_review_list(request):
    """Admin: Review checkouts with filters"""
    # Get filter parameters
    status_filter = request.GET.get('status', 'PENDING')
    sales_user_id = request.GET.get('sales_user', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    month = request.GET.get('month', '')
    year = request.GET.get('year', '')
    
    # Base queryset
    checkouts = ToolCheckout.objects.all().select_related(
        'sales_user', 'tool', 'reviewed_by'
    ).order_by('-created_at')
    
    # Apply filters
    if status_filter and status_filter != 'ALL':
        checkouts = checkouts.filter(status=status_filter)
    
    if sales_user_id:
        checkouts = checkouts.filter(sales_user_id=sales_user_id)
    
    # Date range filter
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            date_from_obj = timezone.make_aware(date_from_obj)
            checkouts = checkouts.filter(created_at__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            date_to_obj = timezone.make_aware(date_to_obj) + timedelta(days=1)
            checkouts = checkouts.filter(created_at__lt=date_to_obj)
        except ValueError:
            pass
    
    # Month/Year filter
    if month and year:
        try:
            month_int = int(month)
            year_int = int(year)
            checkouts = checkouts.filter(
                created_at__month=month_int,
                created_at__year=year_int
            )
        except ValueError:
            pass
    
    # Get all sales users for filter dropdown
    sales_users = User.objects.filter(role='SALES').order_by('full_name')
    
    # Generate year range for filter
    current_year = timezone.now().year
    years = range(current_year - 1, current_year + 2)
    
    return render(request, 'inventory/checkout_review_list.html', {
        'checkouts': checkouts,
        'sales_users': sales_users,
        'years': years,
        'status_filter': status_filter,
        'sales_user_id': sales_user_id,
        'date_from': date_from,
        'date_to': date_to,
        'month': month,
        'year': year,
        'title': 'Review Checkouts'
    })


@admin_required
def checkout_review(request, pk):
    """Admin: Approve/Reject checkout with sales history"""
    checkout = get_object_or_404(ToolCheckout, pk=pk)
    
    # Get sales user's checkout history
    history = ToolCheckout.objects.filter(
        sales_user=checkout.sales_user
    ).exclude(pk=checkout.pk).select_related('tool').order_by('-created_at')[:10]
    
    # Calculate statistics
    stats = {
        'total': ToolCheckout.objects.filter(sales_user=checkout.sales_user).count(),
        'approved': ToolCheckout.objects.filter(sales_user=checkout.sales_user, status='APPROVED').count(),
        'rejected': ToolCheckout.objects.filter(sales_user=checkout.sales_user, status='REJECTED').count(),
        'pending': ToolCheckout.objects.filter(sales_user=checkout.sales_user, status='PENDING').count(),
    }
    
    if request.method == 'POST':
        form = CheckoutReviewForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            admin_notes = form.cleaned_data.get('admin_notes', '')
            
            try:
                with transaction.atomic():
                    if action == 'approve':
                        checkout.approve(admin_user=request.user, admin_notes=admin_notes)
                        messages.success(
                            request,
                            f'Checkout dari {checkout.sales_user.full_name} telah disetujui. Stock "{checkout.tool.name}" berkurang {checkout.quantity} unit.'
                        )
                    else:  # reject
                        checkout.reject(admin_user=request.user, admin_notes=admin_notes)
                        messages.warning(
                            request,
                            f'Checkout dari {checkout.sales_user.full_name} telah ditolak.'
                        )
                
                return redirect('inventory:checkout_review_list')
                
            except ValidationError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, 'Form tidak valid.')
    else:
        form = CheckoutReviewForm()
    
    return render(request, 'inventory/checkout_review.html', {
        'checkout': checkout,
        'form': form,
        'history': history,
        'stats': stats,
        'title': f'Review Checkout - {checkout.sales_user.full_name}'
    })


# Legacy stub views (redirect to new views)
def inventory_list(request):
    return redirect('inventory:tool_list')

def inventory_detail(request, user_pk):
    return redirect('inventory:tool_list')

def inventory_allocate(request, user_pk):
    return redirect('inventory:tool_list')

def my_inventory(request):
    return redirect('inventory:tools_catalog')

def my_inventory_checkout(request):
    return redirect('inventory:tool_checkout')
