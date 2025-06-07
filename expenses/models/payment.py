from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


class Payment(models.Model):
    expense_item = models.ForeignKey("ExpenseItem", on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=13, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)]
    )
    payment_date = models.DateTimeField()
    payment_method = models.ForeignKey(
        "PaymentMethod", 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL
    )
    transaction_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Optional transaction reference (e.g., bank transfer ID, check number, receipt number)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """Validate payment doesn't exceed remaining amount on ExpenseItem"""
        if self.amount and self.expense_item_id:
            remaining = self.expense_item.get_remaining_amount()
            # For existing payments, exclude this payment from remaining calculation
            if self.pk:
                existing_payment = Payment.objects.get(pk=self.pk)
                remaining += existing_payment.amount
            
            if self.amount > remaining:
                raise ValidationError(
                    f"Payment amount ({self.amount}) cannot exceed remaining balance ({remaining})"
                )

    def __str__(self):
        return f"Payment {self.amount} for {self.expense_item.expense.title} on {self.payment_date.date()}"

    class Meta:
        ordering = ["-payment_date", "-created_at"]