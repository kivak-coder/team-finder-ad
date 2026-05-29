from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Настройка админ-панели для кастомной модели User.
    """
    
    # Поля, которые отображаются в списке пользователей
    list_display = (
        'id',             # Используем ID вместо date_joined
        'email', 
        'name', 
        'surname', 
        'phone', 
        'avatar_preview', 
        'is_active', 
        'is_staff',
    )
    
    # Поля, по которым можно фильтровать список справа
    list_filter = (
        'is_active', 
        'is_staff', 
        'is_superuser',
    )
    
    # Поля, по которым работает поиск вверху страницы
    search_fields = (
        'email', 
        'name', 
        'surname', 
        'phone',
    )
    
    # Сортировка по умолчанию (сначала новые — по убыванию ID)
    ordering = ('-id',)
    
    # Поля, которые можно редактировать прямо в списке
    list_editable = ('is_active', 'is_staff')
    
    # Поля, доступные только для чтения
    readonly_fields = ('avatar_preview', 'last_login')
    
    # Разбивка полей на вкладки/секции в форме редактирования
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
            'fields': ('last_login',), # date_joined убран, так как его нет в модели
            'classes': ('collapse',)
        }),
    )
    
    # Поля для формы создания нового пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'name', 'surname', 'phone', 
                'password1', 'password2', 'is_active', 'is_staff'
            ),
        }),
    )
    
    # Кастомный метод для отображения миниатюры аватара в списке
    def avatar_preview(self, obj):
        if obj.avatar and hasattr(obj.avatar, 'url'):
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;">',
                obj.avatar.url
            )
        return '—'
    avatar_preview.short_description = 'Аватар'
