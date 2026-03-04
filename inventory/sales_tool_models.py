from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from PIL import Image
import os


class SalesTool(models.Model):
    """
    Product/tool for sales internal use (separate from customer merchandise)
    Similar to Merchandise but for sales team usage
    """
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text='Nama tool/produk untuk sales'
    )
    description = models.TextField(
        blank=True,
        help_text='Deskripsi tool'
    )
    image = models.ImageField(
        upload_to='sales_tools/%Y/%m/',
        blank=True,
        null=True,
        help_text='Foto tool'
    )
    stock = models.IntegerField(
        default=0,
        help_text='Stock tersedia'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Tool aktif/non-aktif'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_tools',
        help_text='Admin yang membuat tool ini'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sales_tools'
        verbose_name = 'Sales Tool'
        verbose_name_plural = 'Sales Tools'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} (Stock: {self.stock})"
    
    def save(self, *args, **kwargs):
        """Override save to optimize image"""
        super().save(*args, **kwargs)
        
        if self.image:
            try:
                img = Image.open(self.image.path)
                
                # Resize if too large
                max_size = (1200, 1200)
                if img.height > max_size[1] or img.width > max_size[0]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    img.save(self.image.path, quality=85, optimize=True)
            except Exception:
                pass  # Ignore image optimization errors
    
    def deduct_stock(self, quantity):
        """
        Deduct stock (race-condition safe)
        Must be called inside transaction.atomic()
        """
        if quantity <= 0:
            raise ValidationError('Quantity must be greater than 0')
        
        # Lock row for update (race-condition safe)
        tool = SalesTool.objects.select_for_update().get(pk=self.pk)
        
        if tool.stock < quantity:
            raise ValidationError(
                f'Insufficient stock. Available: {tool.stock}, Requested: {quantity}'
            )
        
        tool.stock -= quantity
        tool.save(update_fields=['stock'])
        
        # Refresh current instance
        self.stock = tool.stock
    
    def add_stock(self, quantity):
        """Add stock (race-condition safe)"""
        if quantity <= 0:
            raise ValidationError('Quantity must be greater than 0')
        
        tool = SalesTool.objects.select_for_update().get(pk=self.pk)
        tool.stock += quantity
        tool.save(update_fields=['stock'])
        
        self.stock = tool.stock


class ToolCheckout(models.Model):
    """
    Checkout/request record from sales for tools
    Requires admin approval before stock is deducted
    """
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
    
    # Checkout info
    sales_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='tool_checkouts',
        help_text='Sales user yang checkout'
    )
    tool = models.ForeignKey(
        SalesTool,
        on_delete=models.PROTECT,
        related_name='checkouts',
        help_text='Tool yang di-checkout'
    )
    quantity = models.IntegerField(
        help_text='Jumlah yang di-checkout'
    )
    notes = models.TextField(
        blank=True,
        help_text='Catatan dari sales'
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        help_text='Status checkout'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Waktu checkout'
    )
    
    # Review info (filled when approved/rejected)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_checkouts',
        help_text='Admin yang review'
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Waktu di-review'
    )
    admin_notes = models.TextField(
        blank=True,
        help_text='Catatan dari admin'
    )
    
    class Meta:
        db_table = 'tool_checkouts'
        verbose_name = 'Tool Checkout'
        verbose_name_plural = 'Tool Checkouts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['sales_user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.sales_user.full_name} - {self.tool.name} x{self.quantity} ({self.get_status_display()})"
    
    def clean(self):
        """Validate checkout"""
        super().clean()
        
        if self.quantity <= 0:
            raise ValidationError({'quantity': 'Quantity must be greater than 0'})
        
        # Validate sales_user role
        if self.sales_user_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(pk=self.sales_user_id)
                if not user.is_sales:
                    raise ValidationError({'sales_user': 'User must have SALES role'})
            except User.DoesNotExist:
                pass
    
    def save(self, *args, **kwargs):
        """Override save to run validation"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def approve(self, admin_user, admin_notes=''):
        """
        Approve checkout and deduct stock
        Must be called inside transaction.atomic()
        """
        if self.status != self.Status.PENDING:
            raise ValidationError(f'Cannot approve checkout with status {self.get_status_display()}')
        
        # Deduct stock from tool (race-condition safe)
        self.tool.deduct_stock(self.quantity)
        
        # Update checkout status
        self.status = self.Status.APPROVED
        self.reviewed_by = admin_user
        self.reviewed_at = timezone.now()
        self.admin_notes = admin_notes
        
        # Use update to avoid triggering full_clean again
        ToolCheckout.objects.filter(pk=self.pk).update(
            status=self.status,
            reviewed_by=self.reviewed_by,
            reviewed_at=self.reviewed_at,
            admin_notes=self.admin_notes
        )
    
    def reject(self, admin_user, admin_notes=''):
        """
        Reject checkout (no stock deduction)
        """
        if self.status != self.Status.PENDING:
            raise ValidationError(f'Cannot reject checkout with status {self.get_status_display()}')
        
        self.status = self.Status.REJECTED
        self.reviewed_by = admin_user
        self.reviewed_at = timezone.now()
        self.admin_notes = admin_notes
        
        ToolCheckout.objects.filter(pk=self.pk).update(
            status=self.status,
            reviewed_by=self.reviewed_by,
            reviewed_at=self.reviewed_at,
            admin_notes=self.admin_notes
        )
    
    @property
    def is_pending(self):
        return self.status == self.Status.PENDING
    
    @property
    def is_approved(self):
        return self.status == self.Status.APPROVED
    
    @property
    def is_rejected(self):
        return self.status == self.Status.REJECTED
