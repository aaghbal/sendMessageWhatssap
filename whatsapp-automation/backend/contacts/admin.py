from django.contrib import admin
from .models import PhoneNumber, PhoneNumberGroup


@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('name', 'full_phone_number', 'user', 'is_active', 'created_at')
    list_filter = ('is_active', 'country_code', 'created_at')
    search_fields = ('name', 'phone_number', 'full_phone_number', 'user__email')
    ordering = ('-created_at',)
    readonly_fields = ('full_phone_number', 'created_at', 'updated_at')


@admin.register(PhoneNumberGroup)
class PhoneNumberGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'get_phone_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description', 'user__email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('phone_numbers',)
