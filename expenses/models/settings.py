from django.db import models
from django.core.cache import cache
from typing import Any


class Settings(models.Model):
    """Application-wide settings singleton model."""

    currency = models.CharField(
        max_length=3,
        default='USD',
        help_text='ISO 4217 currency code'
    )

    locale = models.CharField(
        max_length=10,
        default='en_US',
        help_text='Locale identifier (e.g., en_US, fr_FR)'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Settings"
        verbose_name_plural = "Settings"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Ensure only one Settings instance exists."""
        self.pk = 1
        super().save(*args, **kwargs)
        # Clear cache when settings are saved
        cache.delete('app_settings')

    def delete(self, *args: Any, **kwargs: Any) -> None:
        """Prevent deletion of settings."""
        pass

    @classmethod
    def load(cls) -> 'Settings':
        """Load or create settings instance."""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj