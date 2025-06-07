from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date
from django.utils import timezone
from expenses.models import Budget, Expense, ExpenseItem, Month, Payment
from expenses.services import create_expense_items_for_month, check_expense_completion
from expenses.forms import ExpenseForm


def create_paid_expense_item_payment(expense_item, amount=None, payment_date=None):
    """Helper function to create a Payment record for an ExpenseItem."""
    if payment_date is None:
        payment_date = timezone.now()
    if amount is None:
        amount = expense_item.amount
    
    return Payment.objects.create(
        expense_item=expense_item,
        amount=amount,
        payment_date=payment_date,
    )


class InitialInstallmentModelTest(TestCase):
    """Test cases for skip_parts field in Expense model."""

    def setUp(self):
        """Set up test data."""
        self.budget = Budget.objects.create(name="Test Budget", start_date=date.today())

    def test_split_payment_with_skip_parts_validation_success(self):
        """Test valid split payment with skip_parts."""
        expense = Expense(
            budget=self.budget,
            title="Test Split Payment",
            expense_type=Expense.TYPE_SPLIT_PAYMENT,
            amount=Decimal("100.00"),
            total_parts=10,
            skip_parts=5,
            start_date=date.today(),
            day_of_month=date.today().day,
        )
        # Should not raise validation error
        expense.full_clean()

    def test_split_payment_skip_parts_zero_valid(self):
        """Test split payment with skip_parts=0 (default behavior)."""
        expense = Expense(
            budget=self.budget,
            title="Test Split Payment",
            expense_type=Expense.TYPE_SPLIT_PAYMENT,
            amount=Decimal("100.00"),
            total_parts=10,
            skip_parts=0,
            start_date=date.today(),
            day_of_month=date.today().day,
        )
        expense.full_clean()

    def test_split_payment_skip_parts_max_valid(self):
        """Test split payment with skip_parts at maximum (total_parts - 1)."""
        expense = Expense(
            budget=self.budget,
            title="Test Split Payment",
            expense_type=Expense.TYPE_SPLIT_PAYMENT,
            amount=Decimal("100.00"),
            total_parts=10,
            skip_parts=9,
            start_date=date.today(),
            day_of_month=date.today().day,
        )
        expense.full_clean()

    def test_split_payment_skip_parts_negative_invalid(self):
        """Test split payment with negative skip_parts fails validation."""
        expense = Expense(
            budget=self.budget,
            title="Test Split Payment",
            expense_type=Expense.TYPE_SPLIT_PAYMENT,
            amount=Decimal("100.00"),
            total_parts=10,
            skip_parts=-1,
            start_date=date.today(),
            day_of_month=date.today().day,
        )
        with self.assertRaises(ValidationError) as cm:
            expense.full_clean()
        self.assertIn("Skip parts cannot be negative", str(cm.exception))

    def test_split_payment_skip_parts_too_high_invalid(self):
        """Test split payment with skip_parts >= total_parts fails validation."""
        expense = Expense(
            budget=self.budget,
            title="Test Split Payment",
            expense_type=Expense.TYPE_SPLIT_PAYMENT,
            amount=Decimal("100.00"),
            total_parts=10,
            skip_parts=10,
            start_date=date.today(),
            day_of_month=date.today().day,
        )
        with self.assertRaises(ValidationError) as cm:
            expense.full_clean()
        self.assertIn(
            "Skip parts must be less than total parts count", str(cm.exception)
        )

    def test_non_split_payment_with_skip_parts_invalid(self):
        """Test non-split payment with skip_parts > 0 fails validation."""
        expense = Expense(
            budget=self.budget,
            title="Test Recurring",
            expense_type=Expense.TYPE_ENDLESS_RECURRING,
            amount=Decimal("100.00"),
            total_parts=0,
            skip_parts=5,
            start_date=date.today(),
            day_of_month=date.today().day,
        )
        with self.assertRaises(ValidationError) as cm:
            expense.full_clean()
        self.assertIn(
            "Skip parts can only be used with split payment expenses", str(cm.exception)
        )

    def test_non_split_payment_with_zero_skip_parts_valid(self):
        """Test non-split payment with skip_parts=0 is valid."""
        expense = Expense(
            budget=self.budget,
            title="Test Recurring",
            expense_type=Expense.TYPE_ENDLESS_RECURRING,
            amount=Decimal("100.00"),
            total_parts=0,
            skip_parts=0,
            start_date=date.today(),
            day_of_month=date.today().day,
        )
        expense.full_clean()


class InitialInstallmentServiceTest(TestCase):
    """Test cases for skip_parts in service functions."""

    def setUp(self):
        """Set up test data."""
        self.budget = Budget.objects.create(name="Test Budget", start_date=date.today())
        self.month = Month.objects.create(
            budget=self.budget, year=date.today().year, month=date.today().month
        )

    def test_create_expense_items_respects_skip_parts(self):
        """Test that create_expense_items_for_month respects skip_parts."""
        # Create split payment starting from installment 3 (0-based)
        expense = Expense.objects.create(
            budget=self.budget,
            title="Partial Split Payment",
            expense_type=Expense.TYPE_SPLIT_PAYMENT,
            amount=Decimal("100.00"),
            total_parts=10,
            skip_parts=3,
            start_date=date.today(),
            day_of_month=date.today().day,
        )

        # Should create items for remaining 7 installments (10 - 3)
        items = create_expense_items_for_month(expense, self.month)
        self.assertEqual(len(items), 1)  # One item per month call

        # Continue creating items until we reach the limit
        for i in range(6):  # 6 more items to reach 7 total
            month_obj = Month.objects.create(
                budget=self.budget,
                year=2026,  # Use different year to avoid conflicts
                month=i + 1,
            )
            items = create_expense_items_for_month(expense, month_obj)

        # Total items created should be 7 (total_parts - skip_parts)
        total_items = ExpenseItem.objects.filter(expense=expense).count()
        self.assertEqual(total_items, 7)

        # Try to create one more - should not create anything
        extra_month = Month.objects.create(budget=self.budget, year=2027, month=1)
        items = create_expense_items_for_month(expense, extra_month)
        self.assertEqual(len(items), 0)

    def test_check_expense_completion_with_skip_parts(self):
        """Test expense completion logic with skip_parts."""
        expense = Expense.objects.create(
            budget=self.budget,
            title="Partial Split Payment",
            expense_type=Expense.TYPE_SPLIT_PAYMENT,
            amount=Decimal("100.00"),
            total_parts=10,
            skip_parts=7,  # Only 3 installments to pay
            start_date=date.today(),
            day_of_month=date.today().day,
        )

        # Create 3 expense items
        for i in range(3):
            ExpenseItem.objects.create(
                expense=expense,
                month=self.month,
                amount=Decimal("100.00"),
                due_date=date.today(),
            )

        # Should not be complete yet
        self.assertFalse(check_expense_completion(expense))
        self.assertIsNone(expense.closed_at)

        # Pay 2 items - still not complete
        items = ExpenseItem.objects.filter(expense=expense)[:2]
        for item in items:
            create_paid_expense_item_payment(item)

        self.assertFalse(check_expense_completion(expense))

        # Pay the last item - should be complete
        all_items = ExpenseItem.objects.filter(expense=expense)
        remaining_item = next((item for item in all_items if item.status == ExpenseItem.STATUS_PENDING), None)
        self.assertIsNotNone(remaining_item)
        if remaining_item is not None:
            create_paid_expense_item_payment(remaining_item)

        self.assertTrue(check_expense_completion(expense))
        expense.refresh_from_db()
        self.assertIsNotNone(expense.closed_at)


class InitialInstallmentFormTest(TestCase):
    """Test cases for skip_parts in ExpenseForm."""

    def setUp(self):
        """Set up test data."""
        self.budget = Budget.objects.create(name="Test Budget", start_date=date.today())

    def test_form_includes_skip_parts_field(self):
        """Test that form includes skip_parts field."""
        form = ExpenseForm(budget=self.budget)
        self.assertIn("skip_parts", form.fields)

    def test_form_validation_split_payment_valid_skip_parts(self):
        """Test form validation for valid split payment with skip_parts."""
        form_data = {
            "title": "Test Split Payment",
            "expense_type": Expense.TYPE_SPLIT_PAYMENT,
            "amount": "100.00",
            "total_parts": 10,
            "skip_parts": 5,
            "start_date": date.today().strftime("%Y-%m-%d"),
        }
        form = ExpenseForm(data=form_data, budget=self.budget)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_form_validation_split_payment_invalid_skip_parts(self):
        """Test form validation for invalid skip_parts."""
        form_data = {
            "title": "Test Split Payment",
            "expense_type": Expense.TYPE_SPLIT_PAYMENT,
            "amount": "100.00",
            "total_parts": 10,
            "skip_parts": 15,  # Invalid: >= total_parts
            "start_date": date.today().strftime("%Y-%m-%d"),
        }
        form = ExpenseForm(data=form_data, budget=self.budget)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Skip parts must be less than total parts count", str(form.errors)
        )

    def test_form_validation_non_split_payment_with_skip_parts(self):
        """Test form validation for non-split payment with skip_parts."""
        form_data = {
            "title": "Test Recurring",
            "expense_type": Expense.TYPE_ENDLESS_RECURRING,
            "amount": "100.00",
            "total_parts": 0,
            "skip_parts": 5,  # Invalid for non-split payment
            "start_date": date.today().strftime("%Y-%m-%d"),
        }
        form = ExpenseForm(data=form_data, budget=self.budget)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Skip parts can only be used with split payment expenses", str(form.errors)
        )

    def test_form_initial_installment_read_only_on_edit(self):
        """Test that initial_installment field is read-only when editing existing expense."""
        expense = Expense.objects.create(
            budget=self.budget,
            title="Test Split Payment",
            expense_type=Expense.TYPE_SPLIT_PAYMENT,
            amount=Decimal("100.00"),
            total_parts=10,
            skip_parts=5,
            start_date=date.today(),
            day_of_month=date.today().day,
        )

        form = ExpenseForm(instance=expense, budget=self.budget)
        self.assertTrue(form.fields["skip_parts"].disabled)
        self.assertIn(
            "cannot be changed after expense creation",
            form.fields["skip_parts"].help_text,
        )

    def test_form_initial_installment_editable_on_create(self):
        """Test that initial_installment field is editable when creating new expense."""
        form = ExpenseForm(budget=self.budget)
        self.assertFalse(form.fields["skip_parts"].disabled)


class InitialInstallmentIntegrationTest(TestCase):
    """Integration tests for skip_parts feature."""

    def setUp(self):
        """Set up test data."""
        self.budget = Budget.objects.create(name="Test Budget", start_date=date.today())

    def test_complete_workflow_partial_split_payment(self):
        """Test complete workflow for partial split payment."""
        # Create split payment starting from installment 8 out of 10
        expense = Expense.objects.create(
            budget=self.budget,
            title="Car Loan (Started Mid-Term)",
            expense_type=Expense.TYPE_SPLIT_PAYMENT,
            amount=Decimal("500.00"),
            total_parts=10,
            skip_parts=8,  # Only 2 payments remaining
            start_date=date.today(),
            day_of_month=date.today().day,
        )

        # Create first month and generate expense items
        month1 = Month.objects.create(
            budget=self.budget, year=date.today().year, month=date.today().month
        )
        items1 = create_expense_items_for_month(expense, month1)
        self.assertEqual(len(items1), 1)

        # Create second month and generate expense items
        next_month = date.today().month + 1 if date.today().month < 12 else 1
        next_year = (
            date.today().year if date.today().month < 12 else date.today().year + 1
        )

        month2 = Month.objects.create(
            budget=self.budget, year=next_year, month=next_month
        )
        items2 = create_expense_items_for_month(expense, month2)
        self.assertEqual(len(items2), 1)

        # Try third month - should not create any items (only 2 remaining)
        third_month = next_month + 1 if next_month < 12 else 1
        third_year = next_year if next_month < 12 else next_year + 1

        month3 = Month.objects.create(
            budget=self.budget, year=third_year, month=third_month
        )
        items3 = create_expense_items_for_month(expense, month3)
        self.assertEqual(len(items3), 0)

        # Total items should be 2
        total_items = ExpenseItem.objects.filter(expense=expense).count()
        self.assertEqual(total_items, 2)

        # Pay first installment - expense should not be complete
        create_paid_expense_item_payment(items1[0])
        self.assertFalse(check_expense_completion(expense))

        # Pay second installment - expense should be complete
        create_paid_expense_item_payment(items2[0])
        self.assertTrue(check_expense_completion(expense))

        expense.refresh_from_db()
        self.assertIsNotNone(expense.closed_at)
