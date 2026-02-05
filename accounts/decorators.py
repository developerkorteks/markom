from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from functools import wraps

def admin_required(view_func):
    """
    Decorator to ensure user is logged in and has ADMIN role
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.shortcuts import redirect
            from django.conf import settings
            return redirect(settings.LOGIN_URL)
        
        if not request.user.is_admin:
            raise PermissionDenied("You don't have permission to access this page. Admin access required.")
        
        return view_func(request, *args, **kwargs)
    return wrapper

def sales_required(view_func):
    """
    Decorator to ensure user is logged in and has SALES role
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.shortcuts import redirect
            from django.conf import settings
            return redirect(settings.LOGIN_URL)
        
        if not request.user.is_sales:
            raise PermissionDenied("You don't have permission to access this page. Sales access required.")
        
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_or_sales_required(view_func):
    """
    Decorator to ensure user is logged in (either ADMIN or SALES)
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.shortcuts import redirect
            from django.conf import settings
            return redirect(settings.LOGIN_URL)
        
        if not (request.user.is_admin or request.user.is_sales):
            raise PermissionDenied("You don't have permission to access this page.")
        
        return view_func(request, *args, **kwargs)
    return wrapper
