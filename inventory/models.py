from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from merchandise.models import Merchandise


class SalesInventory(models.Model):
    """
    Tracks product allocation per sales user.
    Admin allocates merchandise to sales users.
    Stock is deducted from Merchandise.stock on allocation (Opsi A).
    Sales can checkout from their own allocation.
    """

    sales_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='sales_inventories',
        help_text='Sales user who owns this inventory allocation'
    )
    merchandise = models.ForeignKey(
        Merchandise,
        on_delete=models.PROTECT,
        related_name='sales_inventories',
        help_text='Merchandise allocated to this sales user'
    )
    quantity = models.IntegerField(
        default=0,
        help_text='Current balance of this product for this sales user'
    )
    is_unlimited = models.BooleanField(
        default=False,
        help_text='If True, bypasses all checkout limits'
    )
    max_per_checkout = models.IntegerField(
        null=True,
        blank=True,
        help_text='Maximum quantity per single checkout. Null = unlimited'
    )
    max_daily = models.IntegerField(
        null=True,
        blank=True,
        help_text='Maximum total checkout quantity per day. Null = unlimited'
    )
    daily_used = models.IntegerField(
        default=0,
        help_text='Total quantity checked out today (lazy reset)'
    )
    last_checkout_date = models.DateField(
        null=True,
        blank=True,
        help_text='Date of last checkout, used for daily reset'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sales_inventory'
        verbose_name = 'Sales Inventory'
        verbose_name_plural = 'Sales Inventories'
        ordering = ['sales_user__username', 'merchandise__name']
        unique_together = [('sales_user', 'merchandise')]

    def __str__(self):
        return f"{self.sales_user.username} — {self.merchandise.name} ({self.quantity})"

    def clean(self):
        """Validate model fields."""
        super().clean()

        # Validate sales_user role
        if self.sales_user_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(pk=self.sales_user_id)
                if not user.is_sales:
                    raise ValidationError(
                        {'sales_user': 'User harus memiliki role SALES.'}
                    )
            except User.DoesNotExist:
                pass

        # Validate quantity
        if self.quantity < 0:
            raise ValidationError(
                {'quantity': 'Quantity tidak boleh negatif.'}
            )

        # Validate max_per_checkout
        if self.max_per_checkout is not None and self.max_per_checkout <= 0:
            raise ValidationError(
                {'max_per_checkout': 'Max per checkout harus lebih dari 0.'}
            )

        # Validate max_daily
        if self.max_daily is not None and self.max_daily <= 0:
            raise ValidationError(
                {'max_daily': 'Max harian harus lebih dari 0.'}
            )

        # Validate max_per_checkout <= max_daily (if both set)
        if (self.max_per_checkout is not None and
                self.max_daily is not None and
                self.max_per_checkout > self.max_daily):
            raise ValidationError(
                {'max_per_checkout':
                 'Max per checkout tidak boleh melebihi max harian.'}
            )

        # Validate daily_used
        if self.daily_used < 0:
            raise ValidationError(
                {'daily_used': 'Daily used tidak boleh negatif.'}
            )

    def save(self, *args, **kwargs):
        """Override save to validate."""
        self.full_clean()
        super().save(*args, **kwargs)

    def _reset_daily_if_needed(self):
        """
        Lazy daily reset: if last_checkout_date is not today,
        reset daily_used to 0 and update last_checkout_date.
        Returns current daily_used after potential reset.
        Uses update() to bypass full_clean() for performance.
        """
        today = timezone.localdate()
        if self.last_checkout_date != today:
            self.daily_used = 0
            self.last_checkout_date = today
            SalesInventory.objects.filter(pk=self.pk).update(
                daily_used=0,
                last_checkout_date=today
            )
        return self.daily_used

    def get_daily_remaining(self):
        """
        Returns how many units can still be checked out today.
        Returns None if no daily limit.
        """
        if self.is_unlimited or self.max_daily is None:
            return None
        daily_used = self._reset_daily_if_needed()
        return max(0, self.max_daily - daily_used)

    def can_checkout(self, quantity):
        """
        Validate whether a checkout of `quantity` is allowed.
        Returns (True, '') or (False, 'error message').
        Checks:
        1. quantity > 0
        2. sufficient balance
        3. max_per_checkout limit
        4. max_daily limit (after lazy reset)
        """
        if quantity <= 0:
            return False, 'Quantity harus lebih dari 0.'

        if self.quantity < quantity:
            return False, (
                f'Saldo tidak mencukupi. '
                f'Tersedia: {self.quantity}, Diminta: {quantity}'
            )

        if not self.is_unlimited:
            # Check max_per_checkout
            if self.max_per_checkout is not None:
                if quantity > self.max_per_checkout:
                    return False, (
                        f'Melebihi batas per checkout. '
                        f'Maksimal: {self.max_per_checkout}, Diminta: {quantity}'
                    )

            # Check max_daily (after lazy reset)
            if self.max_daily is not None:
                daily_used = self._reset_daily_if_needed()
                remaining = self.max_daily - daily_used
                if quantity > remaining:
                    return False, (
                        f'Melebihi batas harian. '
                        f'Sisa hari ini: {remaining}, Diminta: {quantity}'
                    )

        return True, ''

    def allocate(self, quantity, performed_by):
        """
        Admin adds allocation to this sales user.
        Deducts from Merchandise.stock (Opsi A).
        Must be called inside transaction.atomic().
        """
        if quantity <= 0:
            raise ValidationError('Quantity alokasi harus lebih dari 0.')

        # Lock SalesInventory row
        fresh = SalesInventory.objects.select_for_update().get(pk=self.pk)
        qty_before = fresh.quantity

        # Deduct from merchandise stock (uses select_for_update internally)
        self.merchandise.deduct_stock(quantity)

        # Add to sales inventory
        new_qty = qty_before + quantity
        SalesInventory.objects.filter(pk=self.pk).update(quantity=new_qty)
        self.quantity = new_qty

        # Record history
        SalesInventoryHistory.objects.create(
            sales_inventory=self,
            sales_user_name=self.sales_user.get_full_name() or self.sales_user.username,
            merchandise_name=self.merchandise.name,
            action=SalesInventoryHistory.Action.ALLOCATE,
            adjustment=quantity,
            qty_before=qty_before,
            qty_after=new_qty,
            performed_by=performed_by
        )

    def reduce(self, quantity, performed_by, notes=''):
        """
        Admin reduces/takes back allocation from sales user.
        Returns stock back to Merchandise.stock (Opsi A).
        Must be called inside transaction.atomic().
        """
        if quantity <= 0:
            raise ValidationError('Quantity pengurangan harus lebih dari 0.')

        # Lock SalesInventory row
        fresh = SalesInventory.objects.select_for_update().get(pk=self.pk)
        qty_before = fresh.quantity

        if qty_before < quantity:
            raise ValidationError(
                f'Saldo sales tidak mencukupi untuk dikurangi. '
                f'Tersedia: {qty_before}, Diminta: {quantity}'
            )

        # Reduce from sales inventory
        new_qty = qty_before - quantity
        SalesInventory.objects.filter(pk=self.pk).update(quantity=new_qty)
        self.quantity = new_qty

        # Return stock to merchandise
        self.merchandise.add_stock(quantity)

        # Record history
        SalesInventoryHistory.objects.create(
            sales_inventory=self,
            sales_user_name=self.sales_user.get_full_name() or self.sales_user.username,
            merchandise_name=self.merchandise.name,
            action=SalesInventoryHistory.Action.REDUCE,
            adjustment=-quantity,
            qty_before=qty_before,
            qty_after=new_qty,
            notes=notes,
            performed_by=performed_by
        )

    def checkout(self, quantity, performed_by, notes=''):
        """
        Sales user checks out from their own allocation.
        Does NOT affect Merchandise.stock (already deducted on allocation).
        Must be called inside transaction.atomic().
        """
        # Validate limits
        ok, error = self.can_checkout(quantity)
        if not ok:
            raise ValidationError(error)

        # Lock SalesInventory row and re-fetch
        fresh = SalesInventory.objects.select_for_update().get(pk=self.pk)

        # Re-validate with locked data
        ok2, error2 = fresh.can_checkout(quantity)
        if not ok2:
            raise ValidationError(error2)

        qty_before = fresh.quantity
        new_qty = qty_before - quantity

        # Update daily_used
        today = timezone.localdate()
        new_daily_used = (fresh.daily_used if fresh.last_checkout_date == today else 0) + quantity

        # Update inventory
        SalesInventory.objects.filter(pk=self.pk).update(
            quantity=new_qty,
            daily_used=new_daily_used,
            last_checkout_date=today
        )
        self.quantity = new_qty
        self.daily_used = new_daily_used
        self.last_checkout_date = today

        # Record history
        SalesInventoryHistory.objects.create(
            sales_inventory=self,
            sales_user_name=self.sales_user.get_full_name() or self.sales_user.username,
            merchandise_name=self.merchandise.name,
            action=SalesInventoryHistory.Action.CHECKOUT,
            adjustment=-quantity,
            qty_before=qty_before,
            qty_after=new_qty,
            notes=notes,
            performed_by=performed_by
        )


class SalesInventoryHistory(models.Model):
    """
    Immutable audit trail for all SalesInventory changes.
    Records every allocate, reduce, and checkout action.
    """

    class Action(models.TextChoices):
        ALLOCATE = 'ALLOCATE', 'Alokasi (Admin)'
        REDUCE   = 'REDUCE',   'Pengurangan (Admin)'
        CHECKOUT = 'CHECKOUT', 'Checkout (Sales)'

    sales_inventory = models.ForeignKey(
        SalesInventory,
        on_delete=models.CASCADE,
        related_name='history',
        help_text='Related sales inventory record'
    )
    sales_user_name = models.CharField(
        max_length=200,
        help_text='Snapshot of sales user name'
    )
    merchandise_name = models.CharField(
        max_length=200,
        help_text='Snapshot of merchandise name'
    )
    action = models.CharField(
        max_length=20,
        choices=Action.choices,
        help_text='Type of action performed'
    )
    adjustment = models.IntegerField(
        help_text='Quantity change: positive for allocate, negative for reduce/checkout'
    )
    qty_before = models.IntegerField(
        help_text='Quantity before this action'
    )
    qty_after = models.IntegerField(
        help_text='Quantity after this action'
    )
    notes = models.TextField(
        blank=True,
        help_text='Optional notes for this action'
    )
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_actions',
        help_text='User who performed this action'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When this action was performed'
    )

    class Meta:
        db_table = 'sales_inventory_history'
        verbose_name = 'Sales Inventory History'
        verbose_name_plural = 'Sales Inventory Histories'
        ordering = ['-created_at']

    def __str__(self):
        return (
            f"{self.get_action_display()} — "
            f"{self.merchandise_name} x {abs(self.adjustment)} "
            f"({self.sales_user_name})"
        )
