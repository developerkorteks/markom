from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Sum
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
        return render(request, 'dashboard/sales_dashboard.html')
