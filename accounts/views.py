from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
from django import forms
from .forms import LoginForm, UserForm, BulkUserImportForm
from .models import User
from .decorators import admin_required
from .bulk_import_utils import parse_csv, validate_csv_data, create_users_bulk
import csv
from io import StringIO

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f'Selamat datang kembali, {user.full_name}!')
                    next_page = request.GET.get('next')
                    if next_page:
                        return redirect(next_page)
                    return redirect('dashboard:home')
                else:
                    messages.error(request, 'Akun Anda telah dinonaktifkan.')
            else:
                messages.error(request, 'Username atau password salah.')
        else:
            messages.error(request, 'Username atau password salah.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Anda berhasil keluar.')
    return redirect('accounts:login')


@login_required
def change_password(request):
    """Force password change for first login"""
    
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        # Validate
        errors = []
        
        if not old_password:
            errors.append('Password lama wajib diisi.')
        elif not request.user.check_password(old_password):
            errors.append('Password lama tidak sesuai.')
        
        if not new_password1:
            errors.append('Password baru wajib diisi.')
        elif len(new_password1) < 6:
            errors.append('Password baru minimal 6 karakter.')
        
        if new_password1 != new_password2:
            errors.append('Konfirmasi password tidak cocok.')
        
        if old_password == new_password1:
            errors.append('Password baru harus berbeda dari password lama.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            # Change password
            request.user.set_password(new_password1)
            request.user.force_password_change = False
            request.user.save()
            
            # Update session to prevent logout
            update_session_auth_hash(request, request.user)
            
            messages.success(request, 'Password berhasil diubah! Silakan melanjutkan.')
            return redirect('dashboard:home')
    
    return render(request, 'accounts/change_password.html', {
        'force_change': request.user.force_password_change if hasattr(request.user, 'force_password_change') else False
    })

@admin_required
def user_list(request):
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    users = User.objects.all()
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    if role_filter:
        users = users.filter(role=role_filter)
    context = {
        'users': users,
        'search_query': search_query,
        'role_filter': role_filter,
        'roles': User.Role.choices
    }
    return render(request, 'accounts/user_list.html', context)

@admin_required
def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST, is_edit=False)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f'Pengguna "{user.full_name}" berhasil dibuat.')
                return redirect('accounts:user_list')
            except Exception as e:
                messages.error(request, f'Gagal membuat pengguna: {str(e)}')
        else:
            messages.error(request, 'Harap perbaiki kesalahan di bawah ini.')
    else:
        form = UserForm(is_edit=False)
    return render(request, 'accounts/user_form.html', {
        'form': form,
        'title': 'Buat Pengguna Baru',
        'button_text': 'Buat Pengguna'
    })

@admin_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user, is_edit=True)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f'Pengguna "{user.full_name}" berhasil diperbarui.')
                return redirect('accounts:user_list')
            except Exception as e:
                messages.error(request, f'Gagal memperbarui pengguna: {str(e)}')
        else:
            messages.error(request, 'Harap perbaiki kesalahan di bawah ini.')
    else:
        form = UserForm(instance=user, is_edit=True)
    return render(request, 'accounts/user_form.html', {
        'form': form,
        'user': user,
        'title': f'Edit Pengguna: {user.full_name}',
        'button_text': 'Perbarui Pengguna'
    })

@admin_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user.pk == request.user.pk:
        messages.error(request, 'Anda tidak dapat menghapus akun sendiri.')
        return redirect('accounts:user_list')
    if request.method == 'POST':
        user_name = user.full_name
        try:
            user.delete()
            messages.success(request, f'Pengguna "{user_name}" berhasil dihapus.')
        except Exception as e:
            messages.error(request, f'Gagal menghapus pengguna: {str(e)}')
        return redirect('accounts:user_list')
    return render(request, 'accounts/user_confirm_delete.html', {'user': user})

@admin_required
def user_toggle_active(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user.pk == request.user.pk:
        messages.error(request, 'Anda tidak dapat menonaktifkan akun sendiri.')
        return redirect('accounts:user_list')
    user.is_active = not user.is_active
    user.save()
    if user.is_active:
        messages.success(request, f'Pengguna "{user.full_name}" berhasil diaktifkan.')
    else:
        messages.success(request, f'Pengguna "{user.full_name}" berhasil dinonaktifkan.')
    return redirect('accounts:user_list')


@admin_required
def bulk_import_users(request):
    """Bulk import sales users from CSV file"""
    
    if request.method == 'POST':
        form = BulkUserImportForm(request.POST, request.FILES)
        
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            
            # Parse CSV
            parsed_data, parse_errors = parse_csv(csv_file)
            
            if parse_errors:
                for error in parse_errors:
                    messages.error(request, error)
                return render(request, 'accounts/bulk_import.html', {'form': form})
            
            # Validate data
            valid_rows, invalid_rows = validate_csv_data(parsed_data)
            
            # Store in session for preview
            request.session['bulk_import_valid'] = valid_rows
            request.session['bulk_import_invalid'] = invalid_rows
            
            # Show preview
            return render(request, 'accounts/bulk_import.html', {
                'form': form,
                'show_preview': True,
                'valid_rows': valid_rows[:10],  # Show first 10
                'invalid_rows': invalid_rows,
                'total_valid': len(valid_rows),
                'total_invalid': len(invalid_rows),
            })
    else:
        form = BulkUserImportForm()
    
    return render(request, 'accounts/bulk_import.html', {'form': form})


@admin_required
def bulk_import_confirm(request):
    """Confirm and execute bulk import"""
    
    if request.method != 'POST':
        messages.error(request, 'Invalid request method.')
        return redirect('accounts:bulk_import')
    
    # Get data from session
    valid_rows = request.session.get('bulk_import_valid', [])
    
    if not valid_rows:
        messages.error(request, 'No data to import. Please upload CSV file first.')
        return redirect('accounts:bulk_import')
    
    # Create users
    success_count, created_users = create_users_bulk(valid_rows)
    
    # Clear session
    request.session.pop('bulk_import_valid', None)
    request.session.pop('bulk_import_invalid', None)
    
    # Store created users in session for download
    request.session['bulk_import_result'] = created_users
    
    messages.success(request, f'Berhasil membuat {success_count} pengguna sales.')
    
    return render(request, 'accounts/bulk_import.html', {
        'show_result': True,
        'success_count': success_count,
        'created_users': created_users,
    })


@admin_required
def bulk_import_download_result(request):
    """Download import result as CSV"""
    
    created_users = request.session.get('bulk_import_result', [])
    
    if not created_users:
        messages.error(request, 'No import result to download.')
        return redirect('accounts:bulk_import')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="import_result.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Username', 'Full Name', 'Email', 'Password'])
    
    for user in created_users:
        writer.writerow([
            user['username'],
            user['full_name'],
            user['email'],
            user['password']
        ])
    
    return response
