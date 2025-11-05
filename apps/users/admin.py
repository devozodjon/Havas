from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils import timezone

from apps.users.models.user import User, VerificationCode
from apps.users.models.device import Device, AppVersion, DeviceType


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'id_display',
        'created_at_display',
        'full_name_display',
        'phone_number',
        'email',
        'device_info_display',
        'last_visit_display',
        'status_display',
        'actions_display'
    ]
    list_filter = [
        'is_active',
        'is_email_verified',
        'is_phone_verified',
        'is_staff',
        'created_at',
        'updated_at'
    ]
    search_fields = [
        'phone_number',
        'email',
        'username',
        'first_name',
        'last_name'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'last_login',
        'password'
    ]

    fieldsets = (
        ('Профиль', {
            'fields': (
                'first_name',
                'last_name',
                'middle_name',
                'date_of_birth'
            )
        }),
        ('Контактная информация', {
            'fields': (
                'phone_number',
                'email',
                'username'
            )
        }),
        ('Статус верификации', {
            'fields': (
                'is_email_verified',
                'is_phone_verified'
            )
        }),
        ('Права и статус', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'is_deleted'
            )
        }),
        ('Временные метки', {
            'fields': (
                'created_at',
                'updated_at',
                'last_login'
            )
        }),
    )

    def id_display(self, obj):
        """Display row number"""
        return f"{obj.id:02d}"

    id_display.short_description = "№"

    def created_at_display(self, obj):
        """Display creation date and time"""
        return obj.created_at.strftime('%H:%M / %d.%m.%Y')

    created_at_display.short_description = "СОЗДАНО"

    def full_name_display(self, obj):
        """Display full name with icon"""
        icon = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" fill="#666"/></svg>'
        return format_html(
            '{} {}',
            mark_safe(icon),
            obj.full_name or 'Не указано'
        )

    full_name_display.short_description = "Ф.И.О"

    def device_info_display(self, obj):
        """Display device type and model"""
        device = obj.devices.filter(is_active=True).first()
        if device:
            return format_html(
                '<div style="line-height: 1.4;">{}<br/><small style="color: #666;">{}</small></div>',
                device.get_device_type_display(),
                device.device_model
            )
        return '-'

    device_info_display.short_description = "УСТРОЙСТВО"

    def last_visit_display(self, obj):
        """Display last visit date"""
        device = obj.devices.filter(is_active=True).first()
        if device and device.last_login:
            return device.last_login.strftime('%H:%M / %d.%m.%Y')
        return '-'

    last_visit_display.short_description = "ПОСЛЕДНЕЕ ПОСЕЩЕНИЕ"

    def status_display(self, obj):
        """Display active status with toggle"""
        if obj.is_active:
            return format_html(
                '<div style="width: 40px; height: 20px; background: #4CAF50; border-radius: 10px; position: relative;">'
                '<div style="width: 16px; height: 16px; background: white; border-radius: 50%; position: absolute; right: 2px; top: 2px;"></div>'
                '</div>'
            )
        else:
            return format_html(
                '<div style="width: 40px; height: 20px; background: #ccc; border-radius: 10px; position: relative;">'
                '<div style="width: 16px; height: 16px; background: white; border-radius: 50%; position: absolute; left: 2px; top: 2px;"></div>'
                '</div>'
            )

    status_display.short_description = "СТАТУС"

    def actions_display(self, obj):
        """Display action buttons"""
        detail_url = reverse('admin:users_user_change', args=[obj.pk])
        return format_html(
            '<a href="{}" style="display: inline-block; width: 32px; height: 32px; background: #FFC107; border-radius: 4px; text-align: center; line-height: 32px; color: white; text-decoration: none; margin-right: 4px;">✎</a>'
            '<a href="#" style="display: inline-block; width: 32px; height: 32px; background: #F44336; border-radius: 4px; text-align: center; line-height: 32px; color: white; text-decoration: none;">🗑</a>',
            detail_url
        )

    actions_display.short_description = "ДЕЙСТВИЯ"

    def get_queryset(self, request):
        """Optimize queryset with related objects"""
        qs = super().get_queryset(request)
        return qs.prefetch_related('devices')


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = [
        'user_display',
        'device_type_icon',
        'device_model',
        'ip_address',
        'last_login_display',
        'is_active_display',
        'firebase_status'
    ]
    list_filter = [
        'device_type',
        'is_active',
        'is_push_notification',
        'theme',
        'language',
        'last_login'
    ]
    search_fields = [
        'device_id',
        'device_model',
        'user__phone_number',
        'user__email',
        'ip_address'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'first_login',
        'last_login',
        'device_token'
    ]

    fieldsets = (
        ('Информация об устройстве', {
            'fields': (
                'device_id',
                'device_type',
                'device_model',
                'operation_version',
                'app_version'
            )
        }),
        ('Пользователь', {
            'fields': ('user',)
        }),
        ('Сетевая информация', {
            'fields': (
                'ip_address',
                'visit_location'
            )
        }),
        ('Настройки', {
            'fields': (
                'language',
                'theme',
                'is_push_notification',
                'is_auth_password'
            )
        }),
        ('Статус сессии', {
            'fields': (
                'is_active',
                'device_token',
                'logged_out_at'
            )
        }),
        ('Firebase', {
            'fields': ('firebase_token',)
        }),
        ('Временные метки', {
            'fields': (
                'first_login',
                'last_login',
                'created_at',
                'updated_at'
            )
        }),
    )

    def user_display(self, obj):
        """Display user info"""
        if obj.user:
            return format_html(
                '<div><strong>{}</strong><br/><small>{}</small></div>',
                obj.user.full_name or 'Не указано',
                obj.user.phone_number or obj.user.email
            )
        return 'Anonymous'

    user_display.short_description = "Пользователь"

    def device_type_icon(self, obj):
        """Display device type with icon"""
        if obj.device_type == DeviceType.ANDROID:
            icon = '🤖'
            color = '#3DDC84'
        else:
            icon = '🍎'
            color = '#000000'
        return format_html(
            '<span style="font-size: 20px;">{}</span>',
            icon
        )

    device_type_icon.short_description = "Тип"

    def last_login_display(self, obj):
        """Display last login time"""
        return obj.last_login.strftime('%H:%M / %d.%m.%Y')

    last_login_display.short_description = "Последнее посещение"

    def is_active_display(self, obj):
        """Display active status"""
        if obj.is_active:
            return format_html(
                '<span style="color: #4CAF50; font-weight: bold;">●</span> Активно'
            )
        return format_html(
            '<span style="color: #F44336; font-weight: bold;">●</span> Неактивно'
        )

    is_active_display.short_description = "Статус"

    def firebase_status(self, obj):
        """Display firebase token status"""
        if obj.firebase_token:
            return format_html(
                '<span style="color: #4CAF50;">✓</span>'
            )
        return format_html(
            '<span style="color: #F44336;">✗</span>'
        )

    firebase_status.short_description = "Firebase"

    actions = ['logout_selected_devices', 'activate_selected_devices']

    def logout_selected_devices(self, request, queryset):
        """Logout selected devices"""
        count = queryset.filter(is_active=True).update(
            is_active=False,
            logged_out_at=timezone.now()
        )
        self.message_user(
            request,
            f'Завершена сессия для {count} устройств.'
        )

    logout_selected_devices.short_description = "Завершить сессию для выбранных устройств"

    def activate_selected_devices(self, request, queryset):
        """Activate selected devices"""
        count = queryset.update(
            is_active=True,
            logged_out_at=None
        )
        self.message_user(
            request,
            f'Активировано {count} устройств.'
        )

    activate_selected_devices.short_description = "Активировать выбранные устройства"


@admin.register(AppVersion)
class AppVersionAdmin(admin.ModelAdmin):
    list_display = [
        'version',
        'device_type',
        'is_active_display',
        'force_update_display',
        'devices_count',
        'created_at'
    ]
    list_filter = [
        'device_type',
        'is_active',
        'force_update',
        'created_at'
    ]
    search_fields = ['version', 'description']

    fieldsets = (
        ('Информация о версии', {
            'fields': (
                'version',
                'device_type',
                'description'
            )
        }),
        ('Настройки', {
            'fields': (
                'is_active',
                'force_update'
            )
        }),
    )

    def is_active_display(self, obj):
        """Display active status"""
        if obj.is_active:
            return format_html(
                '<span style="color: #4CAF50; font-weight: bold;">✓ Активна</span>'
            )
        return format_html(
            '<span style="color: #999;">Неактивна</span>'
        )

    is_active_display.short_description = "Статус"

    def force_update_display(self, obj):
        """Display force update status"""
        if obj.force_update:
            return format_html(
                '<span style="color: #F44336; font-weight: bold;">⚠ Обязательно</span>'
            )
        return format_html(
            '<span style="color: #999;">Опционально</span>'
        )

    force_update_display.short_description = "Обновление"

    def devices_count(self, obj):
        """Count devices using this version"""
        return obj.devices.count()

    devices_count.short_description = "Устройств"


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'code',
        'created_at',
        'is_valid_display',
        'used'
    ]
    list_filter = [
        'used',
        'created_at'
    ]
    search_fields = [
        'code',
        'user__phone_number',
        'user__email'
    ]
    readonly_fields = ['created_at']

    def is_valid_display(self, obj):
        """Display if code is still valid"""
        if obj.is_valid():
            time_left = 15 - int((timezone.now() - obj.created_at).total_seconds() / 60)
            return format_html(
                '<span style="color: #4CAF50;">✓ Действителен ({} мин)</span>',
                time_left
            )
        return format_html(
            '<span style="color: #F44336;">✗ Истек</span>'
        )

    is_valid_display.short_description = "Статус"


# Custom admin site configuration
admin.site.site_header = "HAVAS Администрирование"
admin.site.site_title = "HAVAS Admin"
admin.site.index_title = "Главная страница"