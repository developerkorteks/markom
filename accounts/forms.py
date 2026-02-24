from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User


class LoginForm(AuthenticationForm):
    """Form login kustom dengan styling Bootstrap"""

    username = forms.CharField(
        label='Nama Pengguna',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masukkan nama pengguna',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Kata Sandi',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masukkan kata sandi'
        })
    )


class UserForm(forms.ModelForm):
    """Form untuk membuat dan mengubah pengguna"""

    password1 = forms.CharField(
        label='Kata Sandi',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masukkan kata sandi (kosongkan untuk tidak mengubah)'
        })
    )
    password2 = forms.CharField(
        label='Konfirmasi Kata Sandi',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ulangi kata sandi'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'full_name', 'phone', 'role', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama pengguna untuk login'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Alamat email'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama lengkap pengguna'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nomor telepon (opsional)'
            }),
            'role': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        self.is_edit = kwargs.pop('is_edit', False)
        super().__init__(*args, **kwargs)

        # Wajib isi password untuk pengguna baru
        if not self.is_edit:
            self.fields['password1'].required = True
            self.fields['password2'].required = True
            self.fields['password1'].widget.attrs['placeholder'] = 'Buat kata sandi baru'

    def clean_username(self):
        """Validasi keunikan nama pengguna"""
        username = self.cleaned_data.get('username')

        if self.instance.pk:
            if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
                raise ValidationError('Nama pengguna sudah digunakan.')
        else:
            if User.objects.filter(username=username).exists():
                raise ValidationError('Nama pengguna sudah digunakan.')

        return username

    def clean_email(self):
        """Validasi email"""
        email = self.cleaned_data.get('email')

        if not email:
            raise ValidationError('Email wajib diisi.')

        if self.instance.pk:
            if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
                raise ValidationError('Email sudah digunakan.')
        else:
            if User.objects.filter(email=email).exists():
                raise ValidationError('Email sudah digunakan.')

        return email

    def clean(self):
        """Validasi kata sandi cocok"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 or password2:
            if password1 != password2:
                raise ValidationError({'password2': 'Kata sandi tidak cocok.'})

            if len(password1) < 6:
                raise ValidationError({'password1': 'Kata sandi minimal 6 karakter.'})

        return cleaned_data

    def save(self, commit=True):
        """Simpan pengguna dengan kata sandi"""
        user = super().save(commit=False)

        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)

        if commit:
            user.save()

        return user
