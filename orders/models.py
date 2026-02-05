from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from merchandise.models import Merchandise

class Order(models.Model):
    """
    Order model for customer orders
    No status field - all orders are final once created
    Customer data: name and phone only (no login required for customer)
    """
    order_number = models.CharField(
        max_length=50,
        unique=True,
        help_text='Auto-generated order number (ORD-YYYYMMDD-XXXX)'
    )
    customer_name = models.CharField(
        max_length=200,
        help_text='Customer full name'
    )
    customer_phone = models.CharField(
        max_length=20,
        help_text='Customer WhatsApp number'
    )
    sales_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders',
        help_text='Sales user who created this order'
    )
    notes = models.TextField(
        blank=True,
        help_text='Additional notes or comments'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Order creation timestamp'
    )
    
    class Meta:
        db_table = 'orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order_number} - {self.customer_name}"
    
    def clean(self):
        """Validate order data"""
        super().clean()
        
        # Validate customer name
        if not self.customer_name or not self.customer_name.strip():
            raise ValidationError({'customer_name': 'Customer name is required.'})
        
        # Validate customer phone
        if not self.customer_phone or not self.customer_phone.strip():
            raise ValidationError({'customer_phone': 'Customer phone is required.'})
        
        # Basic phone validation (numbers, +, -, spaces only)
        import re
        phone_clean = re.sub(r'[\s\-\+\(\)]', '', self.customer_phone)
        if not phone_clean.isdigit():
            raise ValidationError({'customer_phone': 'Phone number should contain only digits and valid characters (+, -, spaces).'})
        
        if len(phone_clean) < 10 or len(phone_clean) > 15:
            raise ValidationError({'customer_phone': 'Phone number should be between 10-15 digits.'})
    
    def save(self, *args, **kwargs):
        """Override save to generate order number and validate"""
        # Generate order number if not exists
        if not self.order_number:
            self.order_number = self._generate_order_number()
        
        # Clean data
        self.customer_name = self.customer_name.strip()
        self.customer_phone = self.customer_phone.strip()
        
        # Validate
        self.full_clean()
        
        super().save(*args, **kwargs)
    
    def _generate_order_number(self):
        """Generate unique order number: ORD-YYYYMMDD-XXXX"""
        from django.db.models import Max
        import re
        
        today = timezone.now()
        date_str = today.strftime('%Y%m%d')
        prefix = f'ORD-{date_str}-'
        
        # Get last order number for today
        last_order = Order.objects.filter(
            order_number__startswith=prefix
        ).aggregate(Max('order_number'))['order_number__max']
        
        if last_order:
            # Extract sequence number
            match = re.search(r'-(\d+)$', last_order)
            if match:
                sequence = int(match.group(1)) + 1
            else:
                sequence = 1
        else:
            sequence = 1
        
        return f'{prefix}{sequence:04d}'
    
    @property
    def total_items(self):
        """Get total quantity of all items"""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_unique_items(self):
        """Get count of unique merchandise items"""
        return self.items.count()


class OrderItem(models.Model):
    """
    Order item model for individual merchandise in an order
    Stores merchandise name as snapshot for safety (if merchandise deleted)
    No price field - only quantity tracking
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        help_text='Related order'
    )
    merchandise = models.ForeignKey(
        Merchandise,
        on_delete=models.PROTECT,
        help_text='Merchandise item'
    )
    merchandise_name = models.CharField(
        max_length=200,
        help_text='Merchandise name snapshot'
    )
    quantity = models.IntegerField(
        help_text='Quantity ordered'
    )
    
    class Meta:
        db_table = 'order_items'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.merchandise_name} x {self.quantity}"
    
    def clean(self):
        """Validate order item data"""
        super().clean()
        
        # Validate quantity
        if self.quantity <= 0:
            raise ValidationError({'quantity': 'Quantity must be greater than 0.'})
        
        # Check stock availability
        if self.merchandise:
            if self.merchandise.stock < self.quantity:
                raise ValidationError({
                    'quantity': f'Insufficient stock. Available: {self.merchandise.stock}, Requested: {self.quantity}'
                })
    
    def save(self, *args, **kwargs):
        """Override save to capture merchandise name and validate"""
        # Capture merchandise name as snapshot
        if self.merchandise and not self.merchandise_name:
            self.merchandise_name = self.merchandise.name
        
        # Validate
        self.full_clean()
        
        # Deduct stock automatically
        if not self.pk:  # Only on creation
            self.merchandise.deduct_stock(self.quantity)
        
        super().save(*args, **kwargs)
