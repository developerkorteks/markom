from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from .models import User

class LoginForm(AuthenticationForm):
    """Custom login form with Bootstrap styling"""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )

class UserForm(forms.ModelForm):
    """Form for creating and updating users"""
    
    password1 = forms.CharField(
        label='Password',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password (leave empty to keep current)'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'full_name', 'phone', 'role', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email address'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number (optional)'
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
        
        # Make password required for new users
        if not self.is_edit:
            self.fields['password1'].required = True
            self.fields['password2'].required = True
            self.fields['password1'].widget.attrs['placeholder'] = 'Enter password'
    
    def clean_username(self):
        """Validate username uniqueness"""
        username = self.cleaned_data.get('username')
        
        # Check if username exists (excluding current instance in edit mode)
        if self.instance.pk:
            if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
                raise ValidationError('Username already exists.')
        else:
            if User.objects.filter(username=username).exists():
                raise ValidationError('Username already exists.')
        
        return username
    
    def clean_email(self):
        """Validate email"""
        email = self.cleaned_data.get('email')
        
        if not email:
            raise ValidationError('Email is required.')
        
        # Check if email exists (excluding current instance in edit mode)
        if self.instance.pk:
            if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
                raise ValidationError('Email already exists.')
        else:
            if User.objects.filter(email=email).exists():
                raise ValidationError('Email already exists.')
        
        return email
    
    def clean(self):
        """Validate passwords match"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        # Only validate if passwords are provided
        if password1 or password2:
            if password1 != password2:
                raise ValidationError({'password2': 'Passwords do not match.'})
            
            # Minimum length validation
            if len(password1) < 6:
                raise ValidationError({'password1': 'Password must be at least 6 characters long.'})
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save user with password"""
        user = super().save(commit=False)
        
        # Set password if provided
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        
        if commit:
            user.save()
        
        return user
