from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError


class CustomUserManager(UserManager):
    """Custom user manager to handle superuser creation with correct role"""
    
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """
        Create and save a superuser with ADMIN role
        """
        # Set default values for superuser
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')  # Force ADMIN role for superuser
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        # Email is optional now
        if not email:
            email = ''
        
        return self._create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model with role-based access control
    Roles: ADMIN (Markom) and SALES
    """
    
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin (Markom)'
        SALES = 'SALES', 'Sales'
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.SALES,
        help_text='User role: ADMIN for Markom, SALES for sales team'
    )
    full_name = models.CharField(
        max_length=255,
        help_text='Full name of the user'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text='Phone number'
    )
    force_password_change = models.BooleanField(
        default=False,
        help_text='User must change password on next login'
    )
    
    # Configure fields for createsuperuser command
    REQUIRED_FIELDS = ['full_name']  # email is not required anymore
    EMAIL_FIELD = 'email'  # Email field name (optional)
    
    # Use custom manager
    objects = CustomUserManager()
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        """Check if user is admin"""
        return self.role == self.Role.ADMIN
    
    @property
    def is_sales(self):
        """Check if user is sales"""
        return self.role == self.Role.SALES
    
    def clean(self):
        """Validate user data"""
        super().clean()
        
        # Ensure full_name is provided
        if not self.full_name or not self.full_name.strip():
            raise ValidationError({'full_name': 'Full name is required.'})
        
        # Ensure role is valid
        if self.role not in [self.Role.ADMIN, self.Role.SALES]:
            raise ValidationError({'role': 'Invalid role selected.'})
    
    def save(self, *args, **kwargs):
        """Override save to run validation"""
        self.full_clean()
        super().save(*args, **kwargs)
