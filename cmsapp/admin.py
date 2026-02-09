from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, TimeOffRequest, Holiday

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'location']
    list_filter = ['role', 'country']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'location', 'country')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'location', 'country')}),
    )

@admin.register(TimeOffRequest)
class TimeOffRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'start_date', 'end_date', 'status', 'created_at']
    list_filter = ['status', 'type', 'created_at']
    search_fields = ['user__username', 'user__email', 'reason']
    date_hierarchy = 'created_at'

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'country', 'location']
    list_filter = ['country', 'location', 'date']
    search_fields = ['name']
    date_hierarchy = 'date'