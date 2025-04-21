from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import User, Notification, AppPermission
from .forms import UserRegisterForm, UserLoginForm, UserProfileForm

def home(request):
    """
    Home view that redirects to dashboard if authenticated or shows landing page.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    return render(request, 'core/landing.html')

def login_view(request):
    """
    User login view.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'dashboard:index')
                return redirect(next_url)
            else:
                messages.error(request, 'Email ou senha inválidos.')
    else:
        form = UserLoginForm()
    
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    """
    User logout view.
    """
    logout(request)
    return redirect('core:login')

def register(request):
    """
    User registration view.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard:index')
    else:
        form = UserRegisterForm()
    
    return render(request, 'core/register.html', {'form': form})

@login_required
def profile(request):
    """
    User profile view.
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('core:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'core/profile.html', {'form': form})

@login_required
def notifications(request):
    """
    User notifications view.
    """
    notifications = request.user.notifications.all()
    return render(request, 'core/notifications.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, notification_id):
    """
    Mark a notification as read.
    """
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    if notification.link:
        return redirect(notification.link)
    return redirect('core:notifications')

@login_required
def toggle_theme(request):
    """
    Toggle between light and dark theme.
    """
    user = request.user
    user.dark_mode = not user.dark_mode
    user.save()
    
    # Redirect back to the referring page
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('dashboard:index')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import AppPermission

def landing_page(request):
    """
    View para a página inicial da plataforma.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    return render(request, 'core/landing.html')
