from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib import messages
from accounts.api.tokens import account_activation_token

User = get_user_model()

def activate_account(request, uidb64, token):
    """
    Activate user account and redirect to home page with success message
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, 'Your account has been activated successfully! You can now log in.')
        return redirect('home')
    else:
        messages.error(request, 'Activation link is invalid or has expired.')
        return redirect('home')

def index(request):
    return render(request, 'frontend/index.html')

