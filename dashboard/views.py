from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.utils import timezone
from django.db.models import Count, Sum
from django.core.paginator import Paginator
from orders.models import Order
from merchandise.models import Merchandise
from accounts.models import User


@login_required
def home(request):
    """Dashboard home page - redirects based on role"""
    if request.user.is_admin:
        today = timezone.localdate()
        first_day_of_month = today.replace(day=1)

        # ── Recent orders: last 8, annotated with item_count & total_qty ──
        recent_orders = (
            Order.objects
            .select_related('sales_user')
            .annotate(
                item_count=Count('items', distinct=True),
                total_qty=Sum('items__quantity'),
            )
            .order_by('-created_at')[:8]
        )

        # ── Low stock items list (stock < 10, active only, ordered by stock asc) ──
        low_stock_items = (
            Merchandise.objects
            .filter(stock__lt=10, is_active=True)
            .select_related('category')
            .order_by('stock')[:10]
        )

        # ── Recent stock changes for activity feed ──
        from merchandise.models import StockHistory
        recent_stock_changes = (
            StockHistory.objects
            .select_related('merchandise', 'adjusted_by')
            .order_by('-created_at')[:8]
        )

        # ── Sales performance: order count + total qty per sales user ──
        sales_performance = (
            User.objects
            .filter(role=User.Role.SALES)
            .annotate(
                order_count=Count('orders', distinct=True),
                total_qty=Sum('orders__items__quantity'),
            )
            .order_by('-order_count')
        )

        context = {
            # ── Core counts ──
            'total_orders': Order.objects.count(),
            'total_merchandise': Merchandise.objects.filter(is_active=True).count(),
            'total_sales_users': User.objects.filter(role=User.Role.SALES).count(),

            # ── Stock alerts ──
            'low_stock_count': Merchandise.objects.filter(
                stock__lt=10, is_active=True
            ).count(),
            'out_of_stock_count': Merchandise.objects.filter(
                stock=0, is_active=True
            ).count(),

            # ── Time-based order counts ──
            'orders_today': Order.objects.filter(
                created_at__date=today
            ).count(),
            'orders_this_month': Order.objects.filter(
                created_at__date__gte=first_day_of_month
            ).count(),

            # ── Recent orders widget ──
            'recent_orders': recent_orders,

            # ── Two-column widgets ──
            'low_stock_items': low_stock_items,
            'sales_performance': sales_performance,

            # ── Activity feed: recent stock changes ──
            'recent_stock_changes': recent_stock_changes,
        }
        return render(request, 'dashboard/admin_dashboard.html', context)
    else:
        from orders.cart import Cart

        today = timezone.localdate()
        cart = Cart(request)

        # Stats untuk sales user
        my_orders = Order.objects.filter(sales_user=request.user)
        orders_today = my_orders.filter(created_at__date=today).count()
        total_orders = my_orders.count()

        # Semua produk tersedia — dengan pagination 8 per halaman
        all_products = (
            Merchandise.objects
            .filter(is_active=True, stock__gt=0)
            .select_related('category')
            .order_by('category__name', 'name')
        )
        paginator = Paginator(all_products, 4)
        page_number = request.GET.get('page', 1)
        products_page = paginator.get_page(page_number)

        # Recent orders (5 terakhir)
        recent_orders = (
            my_orders
            .prefetch_related('items')
            .order_by('-created_at')[:5]
        )

        context = {
            'total_orders': total_orders,
            'orders_today': orders_today,
            'products_page': products_page,
            'recent_orders': recent_orders,
            'cart': cart,
            'cart_total': cart.get_total_quantity(),
        }
        return render(request, 'dashboard/sales_dashboard.html', context)


@login_required
def admin_products_json(request):
    """
    AJAX endpoint untuk admin dashboard — produk dengan pagination.
    GET params:
      type: 'tersedia' | 'menipis' | 'habis'
      page: int (default 1)
    """
    if not request.user.is_admin:
        return JsonResponse({'error': 'Akses ditolak.'}, status=403)

    product_type = request.GET.get('type', 'tersedia')
    per_page = 6

    base_qs = Merchandise.objects.select_related('category').filter(is_active=True)

    if product_type == 'tersedia':
        qs = base_qs.filter(stock__gt=0).order_by('category__name', 'name')
    elif product_type == 'menipis':
        qs = base_qs.filter(stock__gt=0, stock__lt=10).order_by('stock', 'name')
        per_page = 5
    elif product_type == 'habis':
        qs = base_qs.filter(stock=0).order_by('name')
        per_page = 5
    else:
        return JsonResponse({'error': 'Tipe tidak valid.'}, status=400)

    paginator = Paginator(qs, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    products_data = []
    for p in page_obj:
        products_data.append({
            'id': p.pk,
            'name': p.name,
            'category': p.category.name if p.category else '',
            'stock': p.stock,
            'is_low_stock': p.is_low_stock,
            'image_url': p.image.url if p.image else '',
            'detail_url': f'/merchandise/{p.pk}/',
            'edit_url': f'/merchandise/{p.pk}/edit/',
            'adjust_url': f'/merchandise/{p.pk}/adjust-stock/',
        })

    return JsonResponse({
        'products': products_data,
        'page': page_obj.number,
        'num_pages': paginator.num_pages,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        'total_count': paginator.count,
        'type': product_type,
    })
