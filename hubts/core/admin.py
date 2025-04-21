from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, AppPermission, Notification

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'profile_image')}),
        ('Preferências', {'fields': ('dark_mode',)}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    
    ordering = ('email',)

class AppPermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'app', 'role')
    list_filter = ('app', 'role')
    search_fields = ('user__email', 'user__username')

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__email', 'title', 'message')
    readonly_fields = ('created_at',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(AppPermission, AppPermissionAdmin)
admin.site.register(Notification, NotificationAdmin)
