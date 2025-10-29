from django.contrib.auth.models import AbstractUser
from datetime import timedelta

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models,transaction
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from apps.shared.models import BaseModel
from apps.users.managers.user import CustomUserManager

import uuid
from django.core.validators import validate_ipv46_address

from apps.shared.exceptions.custom_exceptions import CustomException
from apps.shared.models import BaseModel, Language
from apps.users.managers.device import DeviceManager

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=13, unique=True)
    email = models.EmailField(unique=True)
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username


class VerificationCode(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='verification_codes')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def is_valid(self):
        return (timezone.now() - self.created_at) < timedelta(minutes=15) and not self.used


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """
    Custom user model with flexible authentication fields
    """

    # Authentication fields
    email = models.EmailField(
        max_length=255, unique=True, null=True,
        blank=True, db_index=True
    )

    username = models.CharField(
        max_length=150, unique=True, null=True,
        blank=True, db_index=True
    )

    phone_number = models.CharField(
        max_length=17, unique=True, null=True,
        blank=True, db_index=True
    )

    # Profile fields
    first_name = models.CharField(max_length=64, blank=True, null=True)
    last_name = models.CharField(max_length=64, blank=True, null=True)
    middle_name = models.CharField(max_length=64, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)

    # Status fields
    is_active = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    # This field is used for authentication
    USERNAME_FIELD = 'phone_number'  # Default to phone_number, but can authenticate with any
    REQUIRED_FIELDS = []  # No required fields since we have flexible auth

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email'], name='users_email_idx'),
            models.Index(fields=['username'], name='users_username_idx'),
            models.Index(fields=['phone_number'], name='users_phone_idx')
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(email__isnull=False) |
                      models.Q(username__isnull=False) |
                      models.Q(phone_number__isnull=False),
                name='user_must_have_identifier'
            )
        ]

    @property
    def full_name(self):
        """
        Return the full name for the user
        """
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        if self.username:
            return self.username
        elif self.phone_number:
            return self.phone_number

        return self.email

    def get_tokens(self, access_lifetime=None, refresh_lifetime=None):
        """Generate JWT tokens for the user with optional custom expiration"""
        refresh = RefreshToken.for_user(self)

        # Set custom lifetimes if provided
        if access_lifetime:
            refresh.access_token.set_exp(lifetime=access_lifetime)
        if refresh_lifetime:
            refresh.set_exp(lifetime=refresh_lifetime)

        # Add custom claims
        refresh['email'] = self.email
        refresh['username'] = self.username
        refresh['user_id'] = self.id

        expires_at = timezone.now() + timedelta(seconds=refresh.access_token.lifetime.total_seconds())
        refresh_expires_at = timezone.now() + timedelta(seconds=refresh.lifetime.total_seconds())

        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'token_type': 'Bearer',
            'expires_at': expires_at.isoformat(),
            'refresh_expires_at': refresh_expires_at.isoformat(),
        }


class DeviceTheme(models.TextChoices):
    DARK = "DARK", "Dark"
    LIGHT = "LIGHT", "Light"


class DeviceType(models.TextChoices):
    IOS = "IOS", "iOS"
    ANDROID = "ANDROID", "Android"
    ALL = "ALL", "ALL"


class AppVersion(BaseModel):
    version = models.CharField(max_length=100)
    force_update = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    description = models.TextField(default="")
    device_type = models.CharField(
        max_length=7,
        choices=DeviceType.choices,
        default=DeviceType.ALL,
        db_index=True
    )

    def __str__(self):
        return self.version

    def clean(self):
        """Validate app version rules"""
        # Rule: force_update can only be True if is_active is True
        if self.force_update and not self.is_active:
            raise CustomException(message_key="FORCE_UPDATE_REQUIRES_ACTIVE")

    @transaction.atomic
    def save(self, *args, **kwargs):
        """Override save to run validation and auto-deactivate old versions"""
        # First validate basic rules
        self.clean()

        # If this version is being set as active, deactivate all other active versions
        # for the same device type BEFORE checking for conflicts
        if self.is_active:
            AppVersion.objects.filter(
                device_type=self.device_type,
                is_active=True
            ).exclude(pk=self.pk).update(is_active=False, force_update=False)

        super().save(*args, **kwargs)

    class Meta:
        db_table = 'appversion'
        verbose_name = 'app version'
        verbose_name_plural = 'app versions'


class Device(BaseModel):
    """
    Model to track user devices and manage per-device sessions.
    """
    # Device Information
    device_model = models.CharField(max_length=255, db_index=True)
    operation_version = models.CharField(max_length=155)
    device_type = models.CharField(
        max_length=7,
        choices=DeviceType.choices,
        default=DeviceType.ANDROID,
        db_index=True
    )
    device_id = models.CharField(
        max_length=255,
        db_index=True,
        unique=True,
        help_text="Unique device identifier"
    )
    ip_address = models.GenericIPAddressField(
        validators=[validate_ipv46_address],
        help_text="IP address of the device"
    )
    last_login = models.DateTimeField(auto_now=True, db_index=True)
    first_login = models.DateTimeField(auto_now_add=True)
    visit_location = models.JSONField(
        null=True,
        blank=True,
        help_text="Geographic location data"
    )

    # User Preferences
    language = models.CharField(
        max_length=3,
        choices=Language.choices,
        default=Language.CRL
    )
    theme = models.CharField(
        max_length=5,
        choices=DeviceTheme.choices,
        default=DeviceTheme.LIGHT
    )

    # Status Flags
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Device session is active"
    )
    is_push_notification = models.BooleanField(
        default=True,
        verbose_name="Push Notifications Enabled"
    )
    is_auth_password = models.BooleanField(
        default=False,
        verbose_name="Biometric Authentication Enabled"
    )

    # # Session Management - Critical for per-device logout
    # refresh_token_jti = models.CharField(
    #     max_length=255,
    #     unique=True,
    #     db_index=True,
    #     help_text="JWT refresh token JTI (JWT ID) for this device session"
    # )
    device_token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    logged_out_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When user logged out from this device"
    )

    # Firebase Push Notifications
    firebase_token = models.CharField(
        max_length=500,
        unique=True,
        null=True,
        blank=True,
        db_index=True
    )

    # Relationships
    app_version = models.ForeignKey(
        AppVersion,
        on_delete=models.PROTECT,
        related_name='devices',
        db_index=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="devices",
        db_index=True
    )

    objects = DeviceManager()

    class Meta:
        db_table = 'devices'
        verbose_name = 'Device'
        verbose_name_plural = 'Devices'
        ordering = ['-last_login']
        indexes = [
            models.Index(fields=['user', 'is_active'], name='device_user_active_idx'),
            models.Index(fields=['device_id', 'device_type'], name='device_id_type_idx'),
            # models.Index(fields=['refresh_token_jti', 'is_active'], name='device_token_active_idx'),
            models.Index(fields=['-last_login'], name='device_last_login_idx'),
        ]

    def __str__(self):
        user_info = f"{self.user.username}" if self.user else "Anonymous"
        status = "Active" if self.is_active else "Logged Out"
        return f"{user_info} - {self.device_type} ({self.device_model}) [{status}]"

    def logout(self):
        """
        Logout from this specific device.
        Marks device as inactive and records logout time.
        """
        self.is_active = False
        self.logged_out_at = timezone.now()
        self.save(update_fields=['is_active', 'logged_out_at'])

    def refresh_session(self, new_refresh_token_jti):
        """
        Update device session with new refresh token JTI.
        Called when refresh token is rotated.
        """
        self.refresh_token_jti = new_refresh_token_jti
        self.is_active = True
        self.logged_out_at = None
        self.save(update_fields=['refresh_token_jti', 'is_active', 'logged_out_at', 'last_login'])

    def update_firebase_token(self, token):
        """Update firebase token for push notifications"""
        self.firebase_token = token
        self.save(update_fields=['firebase_token'])

    @classmethod
    def get_active_devices(cls, user):
        """Get all active devices for a user"""
        return cls.objects.filter(user=user, is_active=True).order_by('-last_login')

    @classmethod
    def logout_all_devices(cls, user):
        """Logout from all devices for a user"""
        return cls.objects.filter(user=user, is_active=True).update(
            is_active=False,
            logged_out_at=timezone.now()
        )

    @classmethod
    def logout_other_devices(cls, user, current_device_id):
        """Logout from all devices except current one"""
        return cls.objects.filter(
            user=user,
            is_active=True
        ).exclude(
            id=current_device_id
        ).update(
            is_active=False,
            logged_out_at=timezone.now()
        )

    @classmethod
    def is_token_valid(cls, refresh_token_jti):
        """Check if refresh token JTI is valid (device is active)"""
        return cls.objects.filter(
            refresh_token_jti=refresh_token_jti,
            is_active=True
        ).exists()

    @property
    def is_logged_in(self):
        """Check if device currently has active session"""
        return self.is_active and self.logged_out_at is None

    @property
    def session_duration(self):
        """Calculate how long the session has been active"""
        if self.logged_out_at:
            return self.logged_out_at - self.first_login
        return timezone.now() - self.first_login

    @property
    def display_name(self):
        """Friendly display name for the device"""
        return f"{self.get_device_type_display()} - {self.device_model}"
