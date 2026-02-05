from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    """Dashboard home page - redirects based on role"""
    if request.user.is_admin:
        return render(request, 'dashboard/admin_dashboard.html')
    else:
        return render(request, 'dashboard/sales_dashboard.html')
