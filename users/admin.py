from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Настройка админ-панели для кастомной модели User.
    """
    
    list_display = (
        'id',
        'email', 
        'name', 
        'surname', 
        'phone', 
        'avatar_preview', 
        'is_active', 
        'is_staff',
    )
    
    list_filter = (
        'is_active', 
        'is_staff', 
        'is_superuser',
    )
    
    search_fields = (
        'email', 
        'name', 
        'surname', 
        'phone',
    )
    
    ordering = ('-id',)
    
    list_editable = ('is_active', 'is_staff')
    
    readonly_fields = ('avatar_preview', 'last_login')
    
    fieldsets = (
        ('🔐 Авторизация', {
            'fields': ('email', 'password')
        }),
        ('👤 Личная информация', {
            'fields': ('name', 'surname', 'avatar', 'avatar_preview', 'about')
        }),
        ('📞 Контакты', {
            'fields': ('phone', 'github_url')
        }),
        ('⚙️ Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('📅 Системная информация', {
            'fields': ('last_login',),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'name', 'surname', 'phone', 
                'password1', 'password2', 'is_active', 'is_staff'
            ),
        }),
    )
    
    def avatar_preview(self, obj):
        if obj.avatar and hasattr(obj.avatar, 'url'):
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;">',
                obj.avatar.url
            )
        return '—'
    avatar_preview.short_description = 'Аватар'
