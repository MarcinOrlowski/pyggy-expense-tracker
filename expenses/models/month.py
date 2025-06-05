from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Month(models.Model):
    budget = models.ForeignKey('Budget', on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(2020), MaxValueValidator(2099)]
    )
    month = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['budget', 'year', 'month']
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.year}-{self.month:02d}"

    def has_paid_expenses(self):
        """Check if this month has any paid expense items"""
        return self.expenseitem_set.filter(status='paid').exists()

    def can_be_deleted(self):
        """Check if this month can be deleted (no paid expenses)"""
        return not self.has_paid_expenses()

    @classmethod
    def get_most_recent(cls, budget=None):
        """Get the most recent month in the system or for a specific budget"""
        if budget:
            return cls.objects.filter(budget=budget).first()
        return cls.objects.first()  # Due to ordering, first() returns most recent

    @classmethod
    def get_next_allowed_month(cls, budget=None):
        """Calculate the next month that can be created"""
        most_recent = cls.get_most_recent(budget)
        if not most_recent:
            return None  # No months exist, need initial seeding

        if most_recent.month == 12:
            return {'year': most_recent.year + 1, 'month': 1}
        else:
            return {'year': most_recent.year, 'month': most_recent.month + 1}