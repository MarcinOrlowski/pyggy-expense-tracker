from django.db import models


class Payee(models.Model):
    name = models.CharField(max_length=255, unique=True)
    hidden_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name

    @property
    def is_hidden(self) -> bool:
        return self.hidden_at is not None

    def can_be_deleted(self) -> bool:
        """Check if this payee can be deleted (no associated expenses and not hidden)"""
        return not self.expense_set.exists() and not self.is_hidden

    class Meta:
        ordering = ['name']