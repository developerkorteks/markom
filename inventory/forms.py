from django import forms
from django.core.exceptions import ValidationError
from .models import SalesInventory


class AllocateForm(forms.Form):
    """
    Form for admin to allocate merchandise to a sales user.
    Creates or updates a SalesInventory record.
    """
    quantity = forms.IntegerField(
        min_value=1,
        label='Jumlah Alokasi',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Jumlah yang dialokasikan',
            'min': '1',
        }),
        help_text='Jumlah produk yang akan dialokasikan ke sales ini.'
    )
    is_unlimited = forms.BooleanField(
        required=False,
        label='Unlimited Checkout',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='Jika dicentang, sales dapat checkout berapa saja tanpa batas limit.'
    )
    max_per_checkout = forms.IntegerField(
        required=False,
        min_value=1,
        label='Maks per Checkout',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Kosongkan = tidak ada batas',
            'min': '1',
        }),
        help_text='Jumlah maksimum per sekali checkout. Kosongkan untuk tidak ada batas.'
    )
    max_daily = forms.IntegerField(
        required=False,
        min_value=1,
        label='Maks Harian',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Kosongkan = tidak ada batas',
            'min': '1',
        }),
        help_text='Total maksimum checkout per hari (reset tiap hari). Kosongkan untuk tidak ada batas.'
    )

    def clean(self):
        cleaned_data = super().clean()
        max_per = cleaned_data.get('max_per_checkout')
        max_daily = cleaned_data.get('max_daily')

        if max_per and max_daily and max_per > max_daily:
            raise ValidationError(
                'Maks per checkout tidak boleh melebihi maks harian.'
            )
        return cleaned_data


class UpdateLimitsForm(forms.Form):
    """
    Form for admin to update checkout limits for an existing SalesInventory.
    Does not change quantity — only updates limit settings.
    """
    is_unlimited = forms.BooleanField(
        required=False,
        label='Unlimited Checkout',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='Jika dicentang, sales dapat checkout berapa saja tanpa batas limit.'
    )
    max_per_checkout = forms.IntegerField(
        required=False,
        min_value=1,
        label='Maks per Checkout',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Kosongkan = tidak ada batas',
            'min': '1',
        }),
        help_text='Jumlah maksimum per sekali checkout.'
    )
    max_daily = forms.IntegerField(
        required=False,
        min_value=1,
        label='Maks Harian',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Kosongkan = tidak ada batas',
            'min': '1',
        }),
        help_text='Total maksimum checkout per hari (reset tiap hari).'
    )

    def clean(self):
        cleaned_data = super().clean()
        max_per = cleaned_data.get('max_per_checkout')
        max_daily = cleaned_data.get('max_daily')

        if max_per and max_daily and max_per > max_daily:
            raise ValidationError(
                'Maks per checkout tidak boleh melebihi maks harian.'
            )
        return cleaned_data


class ReduceForm(forms.Form):
    """
    Form for admin to reduce/take back allocation from a sales user.
    Returns stock to Merchandise.stock.
    """
    quantity = forms.IntegerField(
        min_value=1,
        label='Jumlah Pengurangan',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Jumlah yang ditarik kembali',
            'min': '1',
        }),
        help_text='Jumlah produk yang akan ditarik kembali dari sales ini.'
    )
    notes = forms.CharField(
        required=False,
        label='Catatan',
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '2',
            'placeholder': 'Alasan pengurangan (opsional)',
        }),
        help_text='Catatan opsional untuk alasan pengurangan.'
    )

    def __init__(self, *args, max_quantity=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_quantity = max_quantity
        if max_quantity is not None:
            self.fields['quantity'].widget.attrs['max'] = str(max_quantity)
            self.fields['quantity'].help_text = (
                f'Jumlah produk yang akan ditarik kembali. '
                f'Saldo tersedia: {max_quantity}'
            )

    def clean_quantity(self):
        qty = self.cleaned_data.get('quantity')
        if qty and self.max_quantity is not None and qty > self.max_quantity:
            raise ValidationError(
                f'Jumlah melebihi saldo tersedia ({self.max_quantity}).'
            )
        return qty


class CheckoutForm(forms.Form):
    """
    Form for sales user to checkout from their own allocation.
    Validates against SalesInventory limits.
    """
    quantity = forms.IntegerField(
        min_value=1,
        label='Jumlah Checkout',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Jumlah yang diambil',
            'min': '1',
        }),
        help_text='Jumlah produk yang ingin diambil.'
    )
    notes = forms.CharField(
        required=False,
        label='Catatan',
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': '2',
            'placeholder': 'Catatan checkout (opsional)',
        }),
        help_text='Catatan opsional untuk checkout ini.'
    )

    def __init__(self, *args, sales_inventory=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.sales_inventory = sales_inventory
        if sales_inventory is not None:
            inv = sales_inventory
            # Set max berdasarkan saldo
            self.fields['quantity'].widget.attrs['max'] = str(inv.quantity)
            # Set hint berdasarkan limit
            hints = [f'Saldo: {inv.quantity}']
            if not inv.is_unlimited:
                if inv.max_per_checkout:
                    hints.append(f'Maks per checkout: {inv.max_per_checkout}')
                daily_remaining = inv.get_daily_remaining()
                if daily_remaining is not None:
                    hints.append(f'Sisa hari ini: {daily_remaining}')
            self.fields['quantity'].help_text = ' · '.join(hints)

    def clean_quantity(self):
        qty = self.cleaned_data.get('quantity')
        if qty and self.sales_inventory is not None:
            ok, error = self.sales_inventory.can_checkout(qty)
            if not ok:
                raise ValidationError(error)
        return qty
