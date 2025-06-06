from django.test import TestCase
from datetime import date
from expenses.forms.expense import ExpenseForm
from expenses.models import Expense, Budget


class ExpenseFormDefaultsTestCase(TestCase):
    """Test case for verifying default values in expense form"""

    def setUp(self):
        """Set up test data"""
        self.budget = Budget.objects.create(
            name="Test Budget",
            start_date=date.today(),
            initial_amount=1000.00
        )

    def test_new_expense_form_has_default_values(self):
        """Test that new expense form has correct default values"""
        form = ExpenseForm(budget=self.budget)
        
        # Check that expense_type defaults to "one_time"
        self.assertEqual(
            form.fields["expense_type"].initial,
            Expense.TYPE_ONE_TIME,
            "Expense type should default to 'one_time'"
        )
        
        # Check that start_date defaults to current date
        self.assertEqual(
            form.fields["start_date"].initial,
            date.today(),
            "Start date should default to current date"
        )

    def test_existing_expense_form_preserves_values(self):
        """Test that editing existing expense doesn't override with defaults"""
        # Create an existing expense with different values
        expense = Expense.objects.create(
            budget=self.budget,
            title="Test Expense",
            expense_type=Expense.TYPE_ENDLESS_RECURRING,
            amount=100.00,
            start_date=date(2024, 1, 15),
            day_of_month=15
        )
        
        # Create form for editing
        form = ExpenseForm(instance=expense, budget=self.budget)
        
        # Defaults should NOT be applied when editing existing expense
        self.assertNotEqual(
            form.fields["expense_type"].initial,
            Expense.TYPE_ONE_TIME,
            "Expense type should not be overridden when editing existing expense"
        )
        
        self.assertNotEqual(
            form.fields["start_date"].initial,
            date.today(),
            "Start date should not be overridden when editing existing expense"
        )