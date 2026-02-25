from merchandise.models import Merchandise

CART_SESSION_KEY = 'shopping_cart'


class Cart:
    """
    Session-based shopping cart untuk sales user.
    Data disimpan di session dengan format:
    {
        'merchandise_id': {
            'merchandise_id': int,
            'name': str,
            'quantity': int,
            'stock': int,
            'image_url': str or None,
            'category': str,
        },
        ...
    }
    """

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if not isinstance(cart, dict):
            cart = {}
            self.session[CART_SESSION_KEY] = cart
        self.cart = cart

    def _save(self):
        """Mark session as modified so Django saves it."""
        self.session.modified = True

    def add(self, merchandise, quantity=1):
        """
        Tambah merchandise ke keranjang.
        Jika sudah ada, tambah quantity-nya.
        Tidak melebihi stock yang tersedia.
        Returns: (success: bool, message: str)
        """
        key = str(merchandise.pk)
        current_qty = self.cart.get(key, {}).get('quantity', 0)
        new_qty = current_qty + quantity

        if new_qty > merchandise.stock:
            return False, f'Stok tidak mencukupi. Stok tersedia: {merchandise.stock}, di keranjang: {current_qty}'

        if new_qty <= 0:
            self.remove(merchandise.pk)
            return True, 'Item dihapus dari keranjang'

        image_url = None
        try:
            if merchandise.image:
                image_url = merchandise.image.url
        except Exception:
            image_url = None

        self.cart[key] = {
            'merchandise_id': merchandise.pk,
            'name': merchandise.name,
            'quantity': new_qty,
            'stock': merchandise.stock,
            'image_url': image_url,
            'category': merchandise.category.name if merchandise.category else '',
        }
        self._save()
        return True, f'{merchandise.name} ditambahkan ke keranjang'

    def update(self, merchandise_id, quantity):
        """
        Update quantity item tertentu di keranjang.
        Jika quantity <= 0, hapus item.
        Returns: (success: bool, message: str)
        """
        key = str(merchandise_id)
        if key not in self.cart:
            return False, 'Item tidak ada di keranjang'

        if quantity <= 0:
            self.remove(merchandise_id)
            return True, 'Item dihapus dari keranjang'

        # Re-fetch stock terkini dari DB
        try:
            merchandise = Merchandise.objects.get(pk=merchandise_id, is_active=True)
        except Merchandise.DoesNotExist:
            self.remove(merchandise_id)
            return False, 'Produk tidak lagi tersedia'

        if quantity > merchandise.stock:
            return False, f'Stok tidak mencukupi. Stok tersedia: {merchandise.stock}'

        self.cart[key]['quantity'] = quantity
        self.cart[key]['stock'] = merchandise.stock
        self._save()
        return True, 'Jumlah diperbarui'

    def remove(self, merchandise_id):
        """Hapus item dari keranjang."""
        key = str(merchandise_id)
        if key in self.cart:
            del self.cart[key]
            self._save()

    def clear(self):
        """Kosongkan seluruh keranjang."""
        self.session[CART_SESSION_KEY] = {}
        self.cart = self.session[CART_SESSION_KEY]
        self._save()

    def get_items(self):
        """
        Kembalikan list item di keranjang dengan data fresh dari DB.
        Item yang produknya sudah tidak aktif / stok 0 akan di-flag.
        """
        items = []
        keys_to_remove = []

        for key, item_data in self.cart.items():
            try:
                merchandise = Merchandise.objects.select_related('category').get(
                    pk=item_data['merchandise_id']
                )
                qty = item_data['quantity']

                # Update data fresh dari DB
                image_url = None
                try:
                    if merchandise.image:
                        image_url = merchandise.image.url
                except Exception:
                    image_url = None

                items.append({
                    'merchandise_id': merchandise.pk,
                    'merchandise': merchandise,
                    'name': merchandise.name,
                    'category': merchandise.category.name if merchandise.category else '',
                    'quantity': qty,
                    'stock': merchandise.stock,
                    'image_url': image_url,
                    'is_active': merchandise.is_active,
                    'is_available': merchandise.is_active and merchandise.stock >= qty,
                    'is_low_stock': merchandise.is_low_stock,
                    'is_out_of_stock': merchandise.is_out_of_stock,
                })

                # Update cached stock di session
                self.cart[key]['stock'] = merchandise.stock
                self.cart[key]['image_url'] = image_url

            except Merchandise.DoesNotExist:
                keys_to_remove.append(key)

        # Bersihkan item yang produknya sudah dihapus dari DB
        for key in keys_to_remove:
            del self.cart[key]
        if keys_to_remove:
            self._save()

        return items

    def get_total_quantity(self):
        """Total semua item (untuk badge navbar)."""
        return sum(item.get('quantity', 0) for item in self.cart.values())

    def get_total_unique(self):
        """Jumlah jenis produk di keranjang."""
        return len(self.cart)

    def is_empty(self):
        """Cek apakah keranjang kosong."""
        return len(self.cart) == 0

    def has_item(self, merchandise_id):
        """Cek apakah produk tertentu sudah ada di keranjang."""
        return str(merchandise_id) in self.cart

    def get_item_quantity(self, merchandise_id):
        """Ambil quantity item tertentu di keranjang."""
        key = str(merchandise_id)
        return self.cart.get(key, {}).get('quantity', 0)

    def validate(self):
        """
        Validasi semua item sebelum checkout.
        Returns: (is_valid: bool, errors: list[str])
        """
        errors = []
        items = self.get_items()

        if not items:
            errors.append('Keranjang belanja kosong.')
            return False, errors

        for item in items:
            if not item['is_active']:
                errors.append(f"Produk '{item['name']}' sudah tidak tersedia.")
            elif item['stock'] < item['quantity']:
                errors.append(
                    f"Stok '{item['name']}' tidak mencukupi. "
                    f"Tersedia: {item['stock']}, diminta: {item['quantity']}."
                )

        return len(errors) == 0, errors

    def __len__(self):
        return self.get_total_quantity()

    def __iter__(self):
        return iter(self.get_items())
