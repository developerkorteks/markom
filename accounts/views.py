from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .forms import LoginForm, UserForm
from .models import User
from .decorators import admin_required

def login_view(request):
    """Login view"""
    # Redirect if already logged in
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
                    messages.success(request, f'Welcome back, {user.full_name}!')
                    
                    # Redirect to next page or dashboard
                    next_page = request.GET.get('next')
                    if next_page:
                        return redirect(next_page)
                    return redirect('dashboard:home')
                else:
                    messages.error(request, 'Your account has been deactivated.')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')

@admin_required
def user_list(request):
    """List all users (Admin only)"""
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    
    users = User.objects.all()
    
    # Apply search filter
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Apply role filter
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
    """Create new user (Admin only)"""
    if request.method == 'POST':
        form = UserForm(request.POST, is_edit=False)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f'User "{user.full_name}" created successfully.')
                return redirect('accounts:user_list')
            except Exception as e:
                messages.error(request, f'Error creating user: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserForm(is_edit=False)
    
    return render(request, 'accounts/user_form.html', {
        'form': form,
        'title': 'Create New User',
        'button_text': 'Create User'
    })

@admin_required
def user_edit(request, pk):
    """Edit existing user (Admin only)"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user, is_edit=True)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f'User "{user.full_name}" updated successfully.')
                return redirect('accounts:user_list')
            except Exception as e:
                messages.error(request, f'Error updating user: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserForm(instance=user, is_edit=True)
    
    return render(request, 'accounts/user_form.html', {
        'form': form,
        'user': user,
        'title': f'Edit User: {user.full_name}',
        'button_text': 'Update User'
    })

@admin_required
def user_delete(request, pk):
    """Delete user (Admin only)"""
    user = get_object_or_404(User, pk=pk)
    
    # Prevent deleting yourself
    if user.pk == request.user.pk:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('accounts:user_list')
    
    if request.method == 'POST':
        user_name = user.full_name
        try:
            user.delete()
            messages.success(request, f'User "{user_name}" deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting user: {str(e)}')
        return redirect('accounts:user_list')
    
    return render(request, 'accounts/user_confirm_delete.html', {'user': user})

@admin_required
def user_toggle_active(request, pk):
    """Toggle user active status (Admin only)"""
    user = get_object_or_404(User, pk=pk)
    
    # Prevent deactivating yourself
    if user.pk == request.user.pk:
        messages.error(request, 'You cannot deactivate your own account.')
        return redirect('accounts:user_list')
    
    user.is_active = not user.is_active
    user.save()
    
    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'User "{user.full_name}" has been {status}.')
    
    return redirect('accounts:user_list')
