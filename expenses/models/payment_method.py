from django.db import models


class PaymentMethod(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def can_be_deleted(self):
        """Check if this payment method can be deleted (not used in any expense items)"""
        return not self.expenseitem_set.exists()

    class Meta:
        ordering = ['name']