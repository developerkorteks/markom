from django import forms
from django.core.exceptions import ValidationError
from .sales_tool_models import SalesTool, ToolCategory, ToolCheckout


class ToolCategoryForm(forms.ModelForm):
    """Form untuk membuat dan mengubah kategori tools"""

    class Meta:
        model = ToolCategory
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama kategori (contoh: Promosi, Pameran, Display)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Deskripsi kategori (opsional)'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'name': 'Nama Kategori',
            'description': 'Deskripsi',
            'is_active': 'Aktif',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise ValidationError('Nama kategori wajib diisi.')
        # Cek duplikat (case-insensitive)
        qs = ToolCategory.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Kategori dengan nama ini sudah ada.')
        return name


class SalesToolForm(forms.ModelForm):
    """Form for admin to create/edit sales tools"""

    class Meta:
        model = SalesTool
        fields = ['name', 'category', 'description', 'image', 'stock', 'is_unlimited', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama tool'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': '4', 'placeholder': 'Deskripsi tool'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'is_unlimited': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_is_unlimited'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Nama Tool',
            'category': 'Kategori',
            'description': 'Deskripsi',
            'image': 'Foto Tool',
            'stock': 'Stock',
            'is_unlimited': 'Stok Unlimited',
            'is_active': 'Aktif',
        }
        help_texts = {
            'name': 'Nama unik untuk tool ini',
            'category': 'Kategori tool (opsional)',
            'description': 'Deskripsi lengkap tool',
            'image': 'Upload foto tool (opsional)',
            'stock': 'Jumlah stok tersedia',
            'is_unlimited': 'Centang jika tool bisa dipakai berkali-kali tanpa habis (contoh: tenda, spanduk, display stand)',
            'is_active': 'Tool aktif dan bisa di-checkout sales',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = ToolCategory.objects.filter(is_active=True)
        self.fields['category'].empty_label = '-- Tanpa Kategori --'
        self.fields['category'].required = False
        self.fields['stock'].required = False

        # Saat mode edit, pop stock dari form (dikelola via Adjust Stock)
        if self.instance and self.instance.pk:
            self.fields.pop('stock', None)

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        # Cek is_unlimited dari raw POST data (karena clean_stock dipanggil sebelum clean_is_unlimited)
        is_unlimited = bool(self.data.get('is_unlimited'))
        if is_unlimited:
            return 0  # unlimited: stok tidak relevan, simpan 0
        if stock is None:
            raise ValidationError('Stock wajib diisi.')
        if stock < 0:
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
        # Show active tools: either has stock > 0 OR is unlimited
        from django.db.models import Q
        self.fields['tool'].queryset = SalesTool.objects.filter(
            is_active=True
        ).filter(
            Q(is_unlimited=True) | Q(stock__gt=0)
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
