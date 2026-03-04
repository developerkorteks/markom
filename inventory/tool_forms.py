from django import forms
from django.core.exceptions import ValidationError
from .sales_tool_models import SalesTool, ToolCheckout


class SalesToolForm(forms.ModelForm):
    """Form for admin to create/edit sales tools"""
    
    class Meta:
        model = SalesTool
        fields = ['name', 'description', 'image', 'stock', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama tool'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': '4', 'placeholder': 'Deskripsi tool'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Nama Tool',
            'description': 'Deskripsi',
            'image': 'Foto Tool',
            'stock': 'Stock Awal',
            'is_active': 'Aktif',
        }
        help_texts = {
            'name': 'Nama unik untuk tool ini',
            'description': 'Deskripsi lengkap tool',
            'image': 'Upload foto tool (opsional)',
            'stock': 'Jumlah stock awal',
            'is_active': 'Tool aktif dan bisa di-checkout sales',
        }
    
    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise ValidationError('Stock tidak boleh negatif.')
        return stock


class ToolStockAdjustmentForm(forms.Form):
    """Form for admin to adjust tool stock"""
    
    adjustment = forms.IntegerField(
        label='Penyesuaian Stock',
        help_text='Masukkan angka positif untuk menambah, negatif untuk mengurangi',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'contoh: 50 atau -20'})
    )
    reason = forms.CharField(
        label='Alasan',
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': 'Alasan penyesuaian stock'})
    )
    
    def clean_adjustment(self):
        adjustment = self.cleaned_data.get('adjustment')
        if adjustment == 0:
            raise ValidationError('Penyesuaian tidak boleh 0.')
        return adjustment
    
    def clean_reason(self):
        reason = self.cleaned_data.get('reason')
        if not reason or not reason.strip():
            raise ValidationError('Alasan wajib diisi.')
        return reason.strip()


class ToolCheckoutForm(forms.ModelForm):
    """Form for sales to checkout tools"""
    
    class Meta:
        model = ToolCheckout
        fields = ['tool', 'quantity', 'notes']
        widgets = {
            'tool': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': 'Jumlah'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': 'Catatan (opsional)'}),
        }
        labels = {
            'tool': 'Pilih Tool',
            'quantity': 'Jumlah',
            'notes': 'Catatan',
        }
        help_texts = {
            'tool': 'Pilih tool yang ingin di-checkout',
            'quantity': 'Jumlah yang diminta',
            'notes': 'Catatan alasan checkout (opsional)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active tools with stock > 0
        self.fields['tool'].queryset = SalesTool.objects.filter(
            is_active=True,
            stock__gt=0
        ).order_by('name')
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity and quantity <= 0:
            raise ValidationError('Jumlah harus lebih dari 0.')
        return quantity


class CheckoutReviewForm(forms.Form):
    """Form for admin to approve/reject checkout"""
    
    action = forms.ChoiceField(
        choices=[('approve', 'Approve'), ('reject', 'Reject')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Keputusan'
    )
    admin_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '3', 'placeholder': 'Catatan untuk sales (opsional)'}),
        label='Catatan Admin',
        help_text='Catatan opsional untuk sales'
    )
