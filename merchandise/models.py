from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from PIL import Image
import os

class Category(models.Model):
    """
    Category model for organizing merchandise
    Supports soft delete (is_active flag)
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text='Category name (must be unique)'
    )
    description = models.TextField(
        blank=True,
        help_text='Category description'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Active status (soft delete)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def clean(self):
        """Validate category data"""
        super().clean()
        
        # Ensure name is provided and not empty
        if not self.name or not self.name.strip():
            raise ValidationError({'name': 'Category name is required.'})
        
        # Check for duplicate name (case-insensitive)
        qs = Category.objects.filter(name__iexact=self.name.strip())
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError({'name': 'Category with this name already exists.'})
    
    def save(self, *args, **kwargs):
        """Override save to run validation"""
        self.name = self.name.strip()
        self.full_clean()
        super().save(*args, **kwargs)
    
    def delete(self, using=None, keep_parents=False):
        """
        Soft delete: set is_active to False instead of deleting
        Prevent deletion if merchandise still exists
        """
        if self.merchandise_set.exists():
            raise ValidationError(
                'Cannot delete category with existing merchandise. '
                'Please deactivate or move merchandise first.'
            )
        self.is_active = False
        self.save()
    
    @property
    def merchandise_count(self):
        """Count active merchandise in this category"""
        return self.merchandise_set.filter(is_active=True).count()


class Merchandise(models.Model):
    """
    Merchandise model for products
    No price field - only stock tracking
    Supports soft delete (is_active flag)
    """
    name = models.CharField(
        max_length=200,
        help_text='Merchandise name'
    )
    description = models.TextField(
        blank=True,
        help_text='Merchandise description'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        help_text='Category for this merchandise'
    )
    stock = models.IntegerField(
        default=0,
        help_text='Current stock quantity'
    )
    image = models.ImageField(
        upload_to='merchandise/%Y/%m/',
        blank=True,
        null=True,
        help_text='Merchandise image (max 2MB, JPG/PNG)'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Active status (soft delete)'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_merchandise',
        help_text='User who created this merchandise'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'merchandise'
        verbose_name = 'Merchandise'
        verbose_name_plural = 'Merchandise'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} (Stock: {self.stock})"
    
    def clean(self):
        """Validate merchandise data"""
        super().clean()
        
        # Ensure name is provided
        if not self.name or not self.name.strip():
            raise ValidationError({'name': 'Merchandise name is required.'})
        
        # Ensure stock is non-negative
        if self.stock < 0:
            raise ValidationError({'stock': 'Stock cannot be negative.'})
        
        # Validate image size (max 2MB)
        if self.image:
            if self.image.size > 2 * 1024 * 1024:  # 2MB in bytes
                raise ValidationError({'image': 'Image size must be less than 2MB.'})
    
    def save(self, *args, **kwargs):
        """Override save to run validation and optimize image"""
        self.name = self.name.strip()
        self.full_clean()
        
        # Save first to get the file path
        super().save(*args, **kwargs)
        
        # Optimize image if exists
        if self.image:
            self._optimize_image()
    
    def _optimize_image(self):
        """Optimize uploaded image"""
        try:
            img = Image.open(self.image.path)
            
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Resize if too large (max 1200px width)
            max_width = 1200
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Save optimized image
            img.save(self.image.path, quality=85, optimize=True)
        except Exception as e:
            # If optimization fails, just continue (image already saved)
            pass
    
    def delete(self, using=None, keep_parents=False):
        """Soft delete: set is_active to False"""
        self.is_active = False
        self.save()
    
    @property
    def is_low_stock(self):
        """Check if stock is low (less than 10)"""
        return self.stock < 10
    
    @property
    def is_out_of_stock(self):
        """Check if out of stock"""
        return self.stock == 0
    
    def deduct_stock(self, quantity):
        """
        Deduct stock by quantity
        Raises ValidationError if insufficient stock
        """
        if quantity <= 0:
            raise ValidationError('Quantity must be greater than 0.')
        
        if self.stock < quantity:
            raise ValidationError(
                f'Insufficient stock. Available: {self.stock}, Requested: {quantity}'
            )
        
        self.stock -= quantity
        self.save()
    
    def add_stock(self, quantity):
        """Add stock by quantity"""
        if quantity <= 0:
            raise ValidationError('Quantity must be greater than 0.')
        
        self.stock += quantity
        self.save()


class StockHistory(models.Model):
    """
    Stock adjustment history for audit trail
    Tracks manual stock adjustments by admin
    """
    merchandise = models.ForeignKey(
        Merchandise,
        on_delete=models.CASCADE,
        related_name='stock_history',
        help_text='Related merchandise'
    )
    adjustment = models.IntegerField(
        help_text='Stock adjustment amount (positive or negative)'
    )
    stock_before = models.IntegerField(
        help_text='Stock quantity before adjustment'
    )
    stock_after = models.IntegerField(
        help_text='Stock quantity after adjustment'
    )
    reason = models.CharField(
        max_length=200,
        help_text='Reason for adjustment'
    )
    adjusted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        help_text='User who made the adjustment'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stock_history'
        verbose_name = 'Stock History'
        verbose_name_plural = 'Stock History'
        ordering = ['-created_at']
    
    def __str__(self):
        sign = '+' if self.adjustment >= 0 else ''
        return f"{self.merchandise.name}: {sign}{self.adjustment} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
    
    @staticmethod
    def create_adjustment(merchandise, adjustment, reason, adjusted_by):
        """
        Create stock adjustment record
        """
        if adjustment == 0:
            raise ValidationError('Adjustment cannot be zero.')
        
        stock_before = merchandise.stock
        new_stock = stock_before + adjustment
        
        if new_stock < 0:
            raise ValidationError(
                f'Adjustment would result in negative stock. '
                f'Current: {stock_before}, Adjustment: {adjustment}'
            )
        
        # Update merchandise stock
        merchandise.stock = new_stock
        merchandise.save()
        
        # Create history record
        history = StockHistory.objects.create(
            merchandise=merchandise,
            adjustment=adjustment,
            stock_before=stock_before,
            stock_after=new_stock,
            reason=reason,
            adjusted_by=adjusted_by
        )
        
        return history
