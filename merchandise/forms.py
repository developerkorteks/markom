from django import forms
from django.core.exceptions import ValidationError
from .models import Category, Merchandise, StockHistory

class CategoryForm(forms.ModelForm):
    """Form for creating and updating categories"""
    
    class Meta:
        model = Category
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category description (optional)',
                'rows': 3
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def clean_name(self):
        """Validate category name"""
        name = self.cleaned_data.get('name')
        
        if not name or not name.strip():
            raise ValidationError('Category name is required.')
        
        name = name.strip()
        
        # Check for duplicate (case-insensitive)
        qs = Category.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise ValidationError('Category with this name already exists.')
        
        return name


class MerchandiseForm(forms.ModelForm):
    """Form for creating and updating merchandise"""
    
    class Meta:
        model = Merchandise
        fields = ['name', 'description', 'category', 'stock', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter merchandise name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter merchandise description (optional)',
                'rows': 3
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter initial stock',
                'min': 0
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/png,image/jpg'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active categories
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
    
    def clean_name(self):
        """Validate merchandise name"""
        name = self.cleaned_data.get('name')
        
        if not name or not name.strip():
            raise ValidationError('Merchandise name is required.')
        
        return name.strip()
    
    def clean_stock(self):
        """Validate stock"""
        stock = self.cleaned_data.get('stock')
        
        if stock is None:
            raise ValidationError('Stock is required.')
        
        if stock < 0:
            raise ValidationError('Stock cannot be negative.')
        
        return stock
    
    def clean_image(self):
        """Validate image"""
        image = self.cleaned_data.get('image')
        
        if image:
            # Check file size (max 2MB)
            if image.size > 2 * 1024 * 1024:
                raise ValidationError('Image size must be less than 2MB.')
            
            # Check file extension
            ext = image.name.split('.')[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png']:
                raise ValidationError('Only JPG and PNG images are allowed.')
        
        return image


class StockAdjustmentForm(forms.Form):
    """Form for manual stock adjustment"""
    
    adjustment = forms.IntegerField(
        label='Adjustment',
        help_text='Enter positive number to add stock, negative to reduce (e.g., +50 or -20)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., +50 or -20'
        })
    )
    reason = forms.CharField(
        label='Reason',
        max_length=200,
        help_text='Reason for this adjustment',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Restock from supplier, Damaged items'
        })
    )
    
    def clean_adjustment(self):
        """Validate adjustment"""
        adjustment = self.cleaned_data.get('adjustment')
        
        if adjustment == 0:
            raise ValidationError('Adjustment cannot be zero.')
        
        return adjustment
    
    def clean_reason(self):
        """Validate reason"""
        reason = self.cleaned_data.get('reason')
        
        if not reason or not reason.strip():
            raise ValidationError('Reason is required.')
        
        return reason.strip()
