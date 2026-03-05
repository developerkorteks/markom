"""
Middleware for enforcing password change on first login
"""
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages


class ForcePasswordChangeMiddleware:
    """
    Middleware to force users to change password on first login
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs that are allowed even when password change is required
        self.exempt_urls = [
            reverse('accounts:logout'),
            reverse('accounts:login'),
        ]
    
    def __call__(self, request):
        # Check if user is authenticated
        if request.user.is_authenticated:
            # Check if user needs to change password
            if hasattr(request.user, 'force_password_change') and request.user.force_password_change:
                # Get current path
                current_path = request.path
                
                # Check if current URL is exempt
                is_exempt = any(current_path.startswith(url) for url in self.exempt_urls)
                
                # Also exempt password change URL itself
                try:
                    password_change_url = reverse('accounts:change_password')
                    if current_path.startswith(password_change_url):
                        is_exempt = True
                except:
                    pass
                
                # Redirect to password change if not exempt
                if not is_exempt:
                    messages.warning(
                        request,
                        'Anda harus mengganti password sebelum melanjutkan. Ini adalah login pertama Anda.'
                    )
                    return redirect('accounts:change_password')
        
        response = self.get_response(request)
        return response
