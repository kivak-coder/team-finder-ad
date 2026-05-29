from django.contrib import admin
from django.utils.html import format_html
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    Настройка админ-панели для модели Project.
    """
    
    # Поля в списке проектов
    list_display = (
        'name', 
        'owner', 
        'status', 
        'created_at', 
        'participants_count',  # Кастомное поле: кол-во участников
        'github_link',         # Кастомное поле: кликабельная ссылка
    )
    
    # Фильтры справа
    list_filter = (
        'status', 
        'created_at', 
        'owner',
    )
    
    # Поиск по названию и описанию
    search_fields = (
        'name', 
        'description',
        'owner__email',
        'owner__name',
        'owner__surname',
    )
    
    # Сортировка по умолчанию (сначала новые)
    ordering = ('-created_at',)
    
    # Поля, доступные для массового редактирования в списке
    list_editable = ('status',)
    
    # Поля, которые нельзя редактировать (только просмотр)
    readonly_fields = ('created_at', 'owner')
    
    # Поля, которые будут в форме редактирования
    fieldsets = (
        ('📋 Основная информация', {
            'fields': ('name', 'description', 'status')
        }),
        ('🔗 Ссылки', {
            'fields': ('github_url', 'github_link')
        }),
        ('👥 Участники', {
            'fields': ('owner', 'participants'),
            'description': 'Владелец проекта назначается автоматически при создании. '
                          'Участников можно добавлять/удалять через интерфейс ниже.'
        }),
        ('📅 Мета-информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    # Настройка отображения ManyToMany поля (удобный фильтр вместо мульти-селекта)
    filter_horizontal = ('participants',)
    
    # Кастомный метод: количество участников
    def participants_count(self, obj):
        return obj.participants.count()
    participants_count.short_description = 'Участников'
    
    # Кастомный метод: кликабельная ссылка на GitHub
    def github_link(self, obj):
        if obj.github_url:
            return format_html(
                '<a href="{}" target="_blank">Перейти ↗</a>', 
                obj.github_url
            )
        return '—'
    github_link.short_description = 'GitHub'
    
    # Кастомное действие: массово закрыть выбранные проекты
    @admin.action(description='Закрыть выбранные проекты', permissions=['change'])
    def make_closed(self, request, queryset):
        updated = queryset.filter(status='open').update(status='closed')
        self.message_user(request, f'Закрыто проектов: {updated}')
    
    # Добавляем кастомное действие в список доступных
    actions = [make_closed]
    
    # Запрещаем менять владельца проекта после создания
    def has_change_permission(self, request, obj=None):
        if obj and obj.pk and request.user.is_superuser:
            # Суперпользователь может менять всё
            return True
        if obj and obj.pk and request.user == obj.owner:
            # Владелец проекта может редактировать, но не владельца
            return True
        return super().has_change_permission(request, obj)
