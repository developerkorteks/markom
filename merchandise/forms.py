from django import forms
from django.core.exceptions import ValidationError
from .models import Category, Merchandise, StockHistory
import calendar
from datetime import datetime


class CategoryForm(forms.ModelForm):
    """Form untuk membuat dan mengubah kategori"""

    class Meta:
        model = Category
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan nama kategori'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan deskripsi kategori (opsional)',
                'rows': 3
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'name': 'Nama Kategori',
            'description': 'Deskripsi',
            'is_active': 'Aktif',
        }

    def clean_name(self):
        """Validasi nama kategori"""
        name = self.cleaned_data.get('name')

        if not name or not name.strip():
            raise ValidationError('Nama kategori wajib diisi.')

        name = name.strip()

        # Cek duplikat (case-insensitive)
        qs = Category.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError('Kategori dengan nama ini sudah ada.')

        return name


class MerchandiseForm(forms.ModelForm):
    """Form untuk membuat dan mengubah merchandise"""

    class Meta:
        model = Merchandise
        fields = ['name', 'description', 'category', 'stock', 'image', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan nama merchandise'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan deskripsi merchandise (opsional)',
                'rows': 3
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan stok awal',
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
        labels = {
            'name': 'Nama Merchandise',
            'description': 'Deskripsi',
            'category': 'Kategori',
            'stock': 'Stok',
            'image': 'Gambar',
            'is_active': 'Aktif',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hanya tampilkan kategori yang aktif
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        self.fields['category'].empty_label = '-- Pilih Kategori --'

        # Saat mode edit (instance sudah ada), hapus field stock dari form
        # karena stok dikelola melalui fitur Sesuaikan Stok, bukan dari form ini
        if self.instance and self.instance.pk:
            self.fields.pop('stock', None)

    def clean_name(self):
        """Validasi nama merchandise"""
        name = self.cleaned_data.get('name')

        if not name or not name.strip():
            raise ValidationError('Nama merchandise wajib diisi.')

        return name.strip()

    def clean_stock(self):
        """Validasi stok"""
        stock = self.cleaned_data.get('stock')

        if stock is None:
            raise ValidationError('Stok wajib diisi.')

        if stock < 0:
            raise ValidationError('Stok tidak boleh negatif.')

        return stock

    def clean_image(self):
        """Validasi gambar"""
        image = self.cleaned_data.get('image')

        if image:
            # Cek ukuran file (maks 2MB)
            if image.size > 2 * 1024 * 1024:
                raise ValidationError('Ukuran gambar tidak boleh lebih dari 2MB.')

            # Cek ekstensi file
            ext = image.name.split('.')[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png']:
                raise ValidationError('Hanya file JPG dan PNG yang diperbolehkan.')

        return image


class StockAdjustmentForm(forms.Form):
    """Form untuk penyesuaian stok manual"""

    adjustment = forms.IntegerField(
        label='Jumlah Penyesuaian',
        help_text='Masukkan angka positif untuk menambah stok, negatif untuk mengurangi (mis. +10 atau -5)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'mis. +10 atau -5',
        })
    )
    reason = forms.CharField(
        label='Alasan Penyesuaian',
        max_length=200,
        help_text='Jelaskan alasan penyesuaian stok ini',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'mis. Restock dari supplier, Barang rusak, dll.'
        })
    )

    def clean_adjustment(self):
        """Validasi penyesuaian"""
        adjustment = self.cleaned_data.get('adjustment')

        if adjustment == 0:
            raise ValidationError('Jumlah penyesuaian tidak boleh nol.')

        return adjustment

    def clean_reason(self):
        """Validasi alasan"""
        reason = self.cleaned_data.get('reason')

        if not reason or not reason.strip():
            raise ValidationError('Alasan penyesuaian wajib diisi.')

        return reason.strip()


class StockOpnameExportForm(forms.Form):
    """Form untuk export stock opname"""
    
    MONTH_CHOICES = [(i, calendar.month_name[i].upper()) for i in range(1, 13)]
    
    current_year = datetime.now().year
    YEAR_CHOICES = [(year, str(year)) for year in range(current_year - 2, current_year + 2)]
    
    month = forms.ChoiceField(
        choices=MONTH_CHOICES,
        label='Bulan',
        initial=datetime.now().month,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    year = forms.ChoiceField(
        choices=YEAR_CHOICES,
        label='Tahun',
        initial=current_year,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    branch_name = forms.CharField(
        label='Nama Cabang/Organisasi',
        max_length=100,
        initial='SEMARANG',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'mis. SEMARANG, JAKARTA, dll.'
        })
    )
    
    include_sales_tools = forms.BooleanField(
        required=False,
        initial=True,
        label='Sertakan Sales Tools',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def clean_branch_name(self):
        """Validasi branch name"""
        branch_name = self.cleaned_data.get('branch_name')
        
        if not branch_name or not branch_name.strip():
            raise ValidationError('Nama cabang/organisasi wajib diisi.')
        
        return branch_name.strip().upper()
