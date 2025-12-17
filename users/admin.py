from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'phone', 'location', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('GreenGear Information', {
            'fields': ('role', 'phone', 'location', 'workshop_name', 'address')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('GreenGear Information', {
            'fields': ('role', 'phone', 'location', 'workshop_name', 'address')
        }),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)