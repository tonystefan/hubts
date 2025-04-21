from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Custom user model with extended fields for the multi-app platform.
    """
    email = models.EmailField(_('email address'), unique=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    dark_mode = models.BooleanField(default=False)
    
    # Add related names to avoid clashes with auth.User
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name='core_user_set',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='core_user_set',
        related_query_name='user',
    )
    
    def __str__(self):
        return self.email

class AppPermission(models.Model):
    """
    Model to store app-specific permissions for users.
    """
    APP_CHOICES = (
        ('pocos_app', 'Poços de Água'),
        ('caronas_app', 'Caronas'),
    )
    
    ROLE_CHOICES = (
        ('admin', 'Administrador'),
        ('manager', 'Gerente'),
        ('editor', 'Editor'),
        ('viewer', 'Visualizador'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='app_permissions')
    app = models.CharField(max_length=50, choices=APP_CHOICES)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    class Meta:
        unique_together = ('user', 'app')
        verbose_name = 'Permissão de Aplicativo'
        verbose_name_plural = 'Permissões de Aplicativos'
    
    def __str__(self):
        return f"{self.user.email} - {self.get_app_display()} ({self.get_role_display()})"

class Notification(models.Model):
    """
    Model for user notifications.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=100)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
    
    def __str__(self):
        return self.title
