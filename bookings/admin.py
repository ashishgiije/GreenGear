from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'farmer', 'equipment', 'start_date', 'duration', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'start_date', 'created_at', 'duration_type')
    search_fields = ('farmer__username', 'equipment__name', 'farmer__phone')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status',)
    fieldsets = (
        ('Booking Information', {
            'fields': ('farmer', 'equipment', 'start_date', 'duration', 'duration_type')
        }),
        ('Financial Details', {
            'fields': ('total_amount', 'payment_mode')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )