from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models import AppPermission

@login_required
def index(request):
    """
    Dashboard index view showing personalized dashboard for the user.
    """
    # Get user's app permissions
    app_permissions = request.user.app_permissions.all()
    
    # Initialize context with empty data
    context = {
        'pocos_stats': None,
        'caronas_stats': None,
    }
    
    # Check if user has access to pocos_app
    if request.user.is_superuser or app_permissions.filter(app='pocos_app').exists():
        # Placeholder for pocos app statistics
        context['pocos_stats'] = {
            'total_pocos': 0,
            'total_consumo': 0,
            'media_horas': 0,
        }
    
    # Check if user has access to caronas_app
    if request.user.is_superuser or app_permissions.filter(app='caronas_app').exists():
        # Placeholder for caronas app statistics
        context['caronas_stats'] = {
            'total_caronas': 0,
            'total_km': 0,
            'total_economia': 0,
            'saldo': 0,
        }
    
    return render(request, 'dashboard/index.html', context)
