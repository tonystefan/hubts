def app_permissions(request):
    """
    Context processor to add app permissions to all templates.
    This allows the sidebar to show only apps the user has access to.
    """
    context = {
        'user_apps': []
    }
    
    if request.user.is_authenticated:
        # For superusers, show all apps
        if request.user.is_superuser:
            context['user_apps'] = [
                {'id': 'pocos_app', 'name': 'Poços de Água', 'icon': 'water-drop', 'url': '/pocos/'},
                {'id': 'caronas_app', 'name': 'Caronas', 'icon': 'car', 'url': '/caronas/'},
            ]
        else:
            # For regular users, show only apps they have permission for
            app_permissions = request.user.app_permissions.all()
            
            for permission in app_permissions:
                if permission.app == 'pocos_app':
                    context['user_apps'].append({
                        'id': 'pocos_app',
                        'name': 'Poços de Água',
                        'icon': 'water-drop',
                        'url': '/pocos/',
                        'role': permission.role
                    })
                elif permission.app == 'caronas_app':
                    context['user_apps'].append({
                        'id': 'caronas_app',
                        'name': 'Caronas',
                        'icon': 'car',
                        'url': '/caronas/',
                        'role': permission.role
                    })
    
    return context
