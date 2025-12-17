from django.contrib import admin
from .models import Equipment

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'category', 'rent_per_day', 'location', 'availability', 'created_at')
    list_filter = ('category', 'availability', 'created_at')
    search_fields = ('name', 'description', 'location', 'owner__username')
    list_editable = ('availability', 'rent_per_day')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('owner', 'name', 'category', 'description')
        }),
        ('Pricing & Location', {
            'fields': ('rent_per_day', 'rent_per_hour', 'location')
        }),
        ('Status & Images', {
            'fields': ('availability', 'image')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )