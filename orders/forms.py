from django import forms
from django.core.exceptions import ValidationError
from .models import Order, OrderItem
from merchandise.models import Merchandise

class OrderForm(forms.ModelForm):
    """Form for creating orders"""
    
    class Meta:
        model = Order
        fields = ['customer_name', 'customer_phone', 'notes']
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter customer full name',
                'required': True
            }),
            'customer_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 081234567890 or +628123456789',
                'required': True
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Additional notes (optional)',
                'rows': 3
            })
        }
    
    def clean_customer_name(self):
        """Validate customer name"""
        name = self.cleaned_data.get('customer_name')
        
        if not name or not name.strip():
            raise ValidationError('Customer name is required.')
        
        return name.strip()
    
    def clean_customer_phone(self):
        """Validate customer phone"""
        phone = self.cleaned_data.get('customer_phone')
        
        if not phone or not phone.strip():
            raise ValidationError('Customer phone is required.')
        
        # Clean phone number
        import re
        phone_clean = re.sub(r'[\s\-\+\(\)]', '', phone.strip())
        
        if not phone_clean.isdigit():
            raise ValidationError('Phone number should contain only digits and valid characters (+, -, spaces).')
        
        if len(phone_clean) < 10 or len(phone_clean) > 15:
            raise ValidationError('Phone number should be between 10-15 digits.')
        
        return phone.strip()


class OrderItemFormSet(forms.BaseFormSet):
    """Custom formset for order items with validation"""
    
    def clean(self):
        """Validate the formset"""
        if any(self.errors):
            return
        
        if not any(form.cleaned_data and not form.cleaned_data.get('DELETE', False) 
                   for form in self.forms):
            raise ValidationError('At least one item is required.')
        
        # Check for duplicate merchandise
        merchandise_ids = []
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                merchandise = form.cleaned_data.get('merchandise')
                if merchandise:
                    if merchandise.id in merchandise_ids:
                        raise ValidationError(f'Duplicate item: {merchandise.name}. Please combine quantities.')
                    merchandise_ids.append(merchandise.id)


class OrderItemForm(forms.Form):
    """Form for individual order item"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Custom label to show stock info
        self.fields['merchandise'].label_from_instance = lambda obj: f"{obj.name} - {obj.category.name} (Stock: {obj.stock})"
    
    merchandise = forms.ModelChoiceField(
        queryset=Merchandise.objects.filter(is_active=True, stock__gt=0).select_related('category'),
        widget=forms.Select(attrs={
            'class': 'form-select merchandise-select',
            'required': True
        }),
        empty_label='-- Select Merchandise --'
    )
    
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control quantity-input',
            'placeholder': 'Qty',
            'min': 1,
            'required': True
        })
    )
    
    def clean(self):
        """Validate item"""
        cleaned_data = super().clean()
        merchandise = cleaned_data.get('merchandise')
        quantity = cleaned_data.get('quantity')
        
        if merchandise and quantity:
            # Check stock availability
            if merchandise.stock < quantity:
                raise ValidationError(
                    f'Insufficient stock for {merchandise.name}. '
                    f'Available: {merchandise.stock}, Requested: {quantity}'
                )
        
        return cleaned_data


# Create formset
OrderItemFormSet = forms.formset_factory(
    OrderItemForm,
    formset=OrderItemFormSet,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True
)
