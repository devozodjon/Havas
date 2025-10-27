from django.contrib import admin
from apps.users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    fields = ['username', 'phone_number', 'email', 'password', 'is_active', 'first_name', 'last_name']
    readonly_fields = ['password']

