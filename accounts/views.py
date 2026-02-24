from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .forms import LoginForm, UserForm
from .models import User
from .decorators import admin_required

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
