from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from accounts.decorators import sales_required
from merchandise.models import Merchandise
from .cart import Cart


@sales_required
def cart_detail(request):
    """Tampilkan isi keranjang belanja."""
    cart = Cart(request)
    items = cart.get_items()
    context = {
        'cart': cart,
        'items': items,
        'total_quantity': cart.get_total_quantity(),
        'total_unique': cart.get_total_unique(),
    }
    return render(request, 'orders/cart.html', context)


@require_POST
@sales_required
def cart_add(request, merchandise_id):
    """
    Tambah item ke keranjang.
    Mendukung AJAX (returns JSON) dan form biasa (redirect).
    """
    merchandise = get_object_or_404(Merchandise, pk=merchandise_id, is_active=True)
    cart = Cart(request)

    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= 0:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1

    success, msg = cart.add(merchandise, quantity=quantity)

    # AJAX response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': success,
            'message': msg,
            'cart_total_quantity': cart.get_total_quantity(),
            'cart_total_unique': cart.get_total_unique(),
        })

    # Form redirect
    if success:
        messages.success(request, msg)
    else:
        messages.warning(request, msg)

    # Redirect ke halaman sebelumnya atau ke cart
    next_url = request.POST.get('next', '')
    if next_url:
        return redirect(next_url)
    return redirect('orders:cart_detail')


@require_POST
@sales_required
def cart_update(request, merchandise_id):
    """
    Update quantity item di keranjang.
    Mendukung AJAX dan form.
    """
    cart = Cart(request)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    success, msg = cart.update(merchandise_id, quantity)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': success,
            'message': msg,
            'cart_total_quantity': cart.get_total_quantity(),
            'cart_total_unique': cart.get_total_unique(),
            'item_quantity': cart.get_item_quantity(merchandise_id),
        })

    if success:
        messages.success(request, msg)
    else:
        messages.warning(request, msg)
    return redirect('orders:cart_detail')


@require_POST
@sales_required
def cart_remove(request, merchandise_id):
    """Hapus item dari keranjang."""
    cart = Cart(request)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart.remove(merchandise_id)
        return JsonResponse({
            'success': True,
            'message': 'Item dihapus dari keranjang',
            'cart_total_quantity': cart.get_total_quantity(),
            'cart_total_unique': cart.get_total_unique(),
        })

    cart.remove(merchandise_id)
    messages.success(request, 'Item dihapus dari keranjang.')
    return redirect('orders:cart_detail')


@require_POST
@sales_required
def cart_clear(request):
    """Kosongkan seluruh keranjang."""
    cart = Cart(request)
    cart.clear()
    messages.success(request, 'Keranjang berhasil dikosongkan.')
    return redirect('orders:cart_detail')


# ─── Sales-specific views ─────────────────────────────────────────────────────

@sales_required
def my_orders(request):
    """
    Riwayat pesanan untuk sales user — tampilan card-based.
    Filter: search, date_from, date_to.
    """
    from django.db.models import Count, Sum, Q
    from orders.models import Order

    search = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    orders = (
        Order.objects
        .filter(sales_user=request.user)
        .select_related('sales_user')
        .annotate(
            item_count=Count('items'),
            total_quantity=Sum('items__quantity'),
        )
        .order_by('-created_at')
    )

    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(customer_name__icontains=search) |
            Q(customer_phone__icontains=search)
        )
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)

    context = {
        'orders': orders,
        'search': search,
        'date_from': date_from,
        'date_to': date_to,
        'total_count': orders.count(),
    }
    return render(request, 'orders/my_orders.html', context)


# ─── Stub views — akan diimplementasi di Step 6-7 ─────────────────────────────

@sales_required
def shop(request):
    """Katalog produk — stub, diimplementasi di Step 6."""
    from merchandise.models import Merchandise, Category
    from django.db.models import Q

    search = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    sort = request.GET.get('sort', 'name')

    products = Merchandise.objects.filter(is_active=True).select_related('category')

    if search:
        products = products.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    if category_id:
        products = products.filter(category_id=category_id)

    sort_map = {
        'name': 'name',
        'stock_asc': 'stock',
        'stock_desc': '-stock',
        'category': 'category__name',
    }
    products = products.order_by(sort_map.get(sort, 'name'))

    categories = Category.objects.all().order_by('name')
    cart = Cart(request)

    context = {
        'products': products,
        'categories': categories,
        'search': search,
        'category_id': category_id,
        'sort': sort,
        'cart': cart,
    }
    return render(request, 'orders/shop.html', context)


@sales_required
def shop_detail(request, merchandise_id):
    """Detail produk di shop — stub, diimplementasi di Step 7."""
    from merchandise.models import Merchandise
    merchandise = get_object_or_404(Merchandise, pk=merchandise_id, is_active=True)
    cart = Cart(request)
    context = {
        'merchandise': merchandise,
        'cart': cart,
        'cart_quantity': cart.get_item_quantity(merchandise_id),
    }
    return render(request, 'orders/shop_detail.html', context)


@sales_required
def checkout(request):
    """
    Checkout — tampilkan form review + submit order dari keranjang.
    GET  → tampilkan halaman review + form customer info
    POST → validasi, buat Order + OrderItem, kosongkan cart, redirect ke order detail
    """
    from django.db import transaction
    from orders.models import Order, OrderItem

    cart = Cart(request)

    # Cek cart tidak kosong
    if cart.is_empty():
        messages.warning(request, 'Keranjang belanja kosong.')
        return redirect('orders:shop')

    if request.method == 'POST':
        # Ambil data customer dari POST
        customer_name = request.POST.get('customer_name', '').strip()
        customer_phone = request.POST.get('customer_phone', '').strip()
        notes = request.POST.get('notes', '').strip()

        # Validasi input customer
        errors = []
        if not customer_name:
            errors.append('Nama pelanggan wajib diisi.')
        if not customer_phone:
            errors.append('Nomor WhatsApp wajib diisi.')
        else:
            import re as re_module
            phone_clean = re_module.sub(r'[\s\-\+\(\)]', '', customer_phone)
            if not phone_clean.isdigit():
                errors.append('Nomor WhatsApp hanya boleh berisi angka dan karakter +, -, spasi.')
            elif len(phone_clean) < 10 or len(phone_clean) > 15:
                errors.append('Nomor WhatsApp harus antara 10-15 digit.')

        # Validasi cart
        cart_valid, cart_errors = cart.validate()
        if not cart_valid:
            errors.extend(cart_errors)

        if errors:
            for error in errors:
                messages.error(request, error)
            items = cart.get_items()
            return render(request, 'orders/checkout.html', {
                'cart': cart,
                'items': items,
                'total_quantity': cart.get_total_quantity(),
                'total_unique': cart.get_total_unique(),
                'customer_name': customer_name,
                'customer_phone': customer_phone,
                'notes': notes,
            })

        # Buat order dengan transaction atomic
        try:
            with transaction.atomic():
                order = Order(
                    customer_name=customer_name,
                    customer_phone=customer_phone,
                    notes=notes,
                    sales_user=request.user,
                )
                order.save()

                # Buat order items dari cart
                items = cart.get_items()
                for item in items:
                    OrderItem.objects.create(
                        order=order,
                        merchandise=item['merchandise'],
                        quantity=item['quantity'],
                    )

            # Kosongkan cart setelah berhasil
            cart.clear()
            messages.success(
                request,
                f'Pesanan {order.order_number} berhasil dibuat! '
                f'{len(items)} jenis produk telah dipesan.'
            )
            return redirect('orders:order_detail', pk=order.pk)

        except Exception as e:
            messages.error(request, f'Gagal membuat pesanan: {str(e)}')
            items = cart.get_items()
            return render(request, 'orders/checkout.html', {
                'cart': cart,
                'items': items,
                'total_quantity': cart.get_total_quantity(),
                'total_unique': cart.get_total_unique(),
                'customer_name': customer_name,
                'customer_phone': customer_phone,
                'notes': notes,
            })

    # GET — tampilkan halaman review
    # Validasi cart dulu
    is_valid, cart_errors = cart.validate()
    if not is_valid:
        for error in cart_errors:
            messages.error(request, error)
        return redirect('orders:cart_detail')

    items = cart.get_items()
    context = {
        'cart': cart,
        'items': items,
        'total_quantity': cart.get_total_quantity(),
        'total_unique': cart.get_total_unique(),
    }
    return render(request, 'orders/checkout.html', context)
