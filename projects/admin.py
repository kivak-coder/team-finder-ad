from django.contrib import admin
from django.utils.html import format_html
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    
    list_display = (
        'name', 
        'owner', 
        'status', 
        'created_at', 
        'participants_count',
        'github_link',
    )
    
    list_filter = (
        'status', 
        'created_at', 
        'owner',
    )
    
    search_fields = (
        'name', 
        'description',
        'owner__email',
        'owner__name',
        'owner__surname',
    )
    
    ordering = ('-created_at',)
    
    list_editable = ('status',)
    
    readonly_fields = ('created_at', 'owner')
    
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
    
    filter_horizontal = ('participants',)
    
    def participants_count(self, obj):
        return obj.participants.count()
    participants_count.short_description = 'Участников'
    
    def github_link(self, obj):
        if obj.github_url:
            return format_html(
                '<a href="{}" target="_blank">Перейти ↗</a>', 
                obj.github_url
            )
        return '—'
    github_link.short_description = 'GitHub'
    
    @admin.action(description='Закрыть выбранные проекты', permissions=['change'])
    def make_closed(self, request, queryset):
        updated = queryset.filter(status='open').update(status='closed')
        self.message_user(request, f'Закрыто проектов: {updated}')
    
    actions = [make_closed]
    
    def has_change_permission(self, request, obj=None):
        if obj and obj.pk and request.user.is_superuser:
            return True
        if obj and obj.pk and request.user == obj.owner:
            return True
        return super().has_change_permission(request, obj)
