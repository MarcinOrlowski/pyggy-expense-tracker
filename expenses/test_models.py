from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date, datetime, timedelta
from expenses.models import (
    Budget,
    Payee,
    PaymentMethod,
    Payment,
    BudgetMonth,
    Expense,
    ExpenseItem,
    Settings,
)


def create_paid_expense_item(expense, month, due_date, amount, payment_date=None):
    """Helper function to create a paid ExpenseItem with Payment record."""
    if payment_date is None:
        payment_date = timezone.now()
    
    expense_item = ExpenseItem.objects.create(
        expense=expense,
        month=month,
        due_date=due_date,
        amount=amount,
    )
    Payment.objects.create(
        expense_item=expense_item,
        amount=amount,
        payment_date=payment_date,
    )
    return expense_item


class PayeeModelTest(TestCase):
    """Test cases for Payee model methods and properties."""

    def setUp(self):
        """Set up test data."""
        self.payee = Payee.objects.create(name="Test Payee")
        self.hidden_payee = Payee.objects.create(
            name="Hidden Payee", hidden_at=timezone.now()
        )

    def test_payee_str_representation(self):
        """Test string representation of payee."""
        self.assertEqual(str(self.payee), "Test Payee")

    def test_is_hidden_property(self):
        """Test is_hidden property."""
        self.assertFalse(self.payee.is_hidden)
        self.assertTrue(self.hidden_payee.is_hidden)

    def test_can_be_deleted_with_no_expenses(self):
        """Test can_be_deleted when payee has no expenses."""
        self.assertTrue(self.payee.can_be_deleted())

    def test_can_be_deleted_when_hidden(self):
        """Test can_be_deleted returns False when payee is hidden."""
        self.assertFalse(self.hidden_payee.can_be_deleted())

    def test_can_be_deleted_with_expenses(self):
        """Test can_be_deleted when payee has expenses."""
        budget = Budget.objects.create(name="Test Budget", start_date=date.today())
        expense = Expense.objects.create(
            budget=budget,
            title="Test Expense",
            payee=self.payee,
            expense_type="endless_recurring",
            amount=Decimal("100.00"),
            start_date=date.today(),
            day_of_month=date.today().day,
        )
        self.assertFalse(self.payee.can_be_deleted())


class PaymentMethodModelTest(TestCase):
    """Test cases for PaymentMethod model."""

    def test_payment_method_str_representation(self):
        """Test string representation of payment method."""
        method = PaymentMethod.objects.create(name="Credit Card")
        self.assertEqual(str(method), "Credit Card")

    def test_payment_method_ordering(self):
        """Test that payment methods are ordered by name."""
        PaymentMethod.objects.create(name="Debit Card")
        PaymentMethod.objects.create(name="Cash")
        PaymentMethod.objects.create(name="Bank Transfer")

        methods = list(PaymentMethod.objects.values_list("name", flat=True))
        self.assertEqual(methods, ["Bank Transfer", "Cash", "Debit Card"])


class ExpenseModelTest(TestCase):
    """Test cases for Expense model methods."""

    def setUp(self):
        """Set up test data."""
        self.budget = Budget.objects.create(name="Test Budget", start_date=date.today())
        self.payee = Payee.objects.create(name="Test Payee")
        self.expense_with_payee = Expense.objects.create(
            budget=self.budget,
            title="Rent",
            payee=self.payee,
            expense_type="endless_recurring",
            amount=Decimal("1000.00"),
            start_date=date.today(),
            day_of_month=date.today().day,
        )
        self.expense_without_payee = Expense.objects.create(
            budget=self.budget,
            title="Subscription",
            payee=None,
            expense_type="endless_recurring",
            amount=Decimal("50.00"),
            start_date=date.today(),
            day_of_month=date.today().day,
        )

    def test_expense_str_with_payee(self):
        """Test string representation with payee."""
        self.assertEqual(str(self.expense_with_payee), "Rent - Test Payee")

    def test_expense_str_without_payee(self):
        """Test string representation without payee."""
        self.assertEqual(str(self.expense_without_payee), "Subscription")

    def test_get_expense_type_icon(self):
        """Test expense type icon mapping."""
        # Test all expense types
        test_cases = [
            ("endless_recurring", "fa-arrows-rotate"),
            ("split_payment", "fa-money-bill-transfer"),
            ("one_time", "fa-circle-dot"),
            ("recurring_with_end", "fa-calendar-check"),
        ]

        for expense_type, expected_icon in test_cases:
            self.expense_with_payee.expense_type = expense_type
            self.assertEqual(
                self.expense_with_payee.get_expense_type_icon(),
                expected_icon,
                f"Icon for {expense_type} should be {expected_icon}",
            )

    def test_get_expense_type_icon_default(self):
        """Test default icon for unknown expense type."""
        self.expense_with_payee.expense_type = "unknown_type"
        self.assertEqual(
            self.expense_with_payee.get_expense_type_icon(), "fa-question-circle"
        )


class ExpenseItemModelTest(TestCase):
    """Test cases for ExpenseItem model methods."""

    def setUp(self):
        """Set up test data."""
        self.budget = Budget.objects.create(name="Test Budget", start_date=date.today())
        self.month = BudgetMonth.objects.create(
            budget=self.budget, year=date.today().year, month=date.today().month
        )
        self.expense = Expense.objects.create(
            budget=self.budget,
            title="Test Expense",
            expense_type="endless_recurring",
            amount=Decimal("100.00"),
            start_date=date.today(),
            day_of_month=date.today().day,
        )

    def test_expense_item_str_representation(self):
        """Test string representation of expense item."""
        item = ExpenseItem.objects.create(
            expense=self.expense,
            month=self.month,
            amount=Decimal("100.00"),
            due_date=date.today(),

        )
        expected = f"Test Expense - {self.month} - pending"
        self.assertEqual(str(item), expected)

    def test_days_until_due_future(self):
        """Test days_until_due for future due date."""
        future_date = date.today() + timedelta(days=10)
        item = ExpenseItem.objects.create(
            expense=self.expense,
            month=self.month,
            amount=Decimal("100.00"),
            due_date=future_date,

        )
        self.assertEqual(item.days_until_due, 10)

    def test_days_until_due_today(self):
        """Test days_until_due for today."""
        item = ExpenseItem.objects.create(
            expense=self.expense,
            month=self.month,
            amount=Decimal("100.00"),
            due_date=date.today(),

        )
        self.assertEqual(item.days_until_due, 0)

    def test_days_until_due_past(self):
        """Test days_until_due for past due date."""
        past_date = date.today() - timedelta(days=5)
        item = ExpenseItem.objects.create(
            expense=self.expense,
            month=self.month,
            amount=Decimal("100.00"),
            due_date=past_date,

        )
        self.assertEqual(item.days_until_due, -5)


class SettingsModelTest(TestCase):
    """Test cases for Settings model."""

    def setUp(self):
        """Clear any existing settings."""
        Settings.objects.all().delete()

    def test_settings_creation(self):
        """Test creating settings instance."""
        settings = Settings.objects.create(locale="en_US", currency="USD")
        self.assertEqual(settings.locale, "en_US")
        self.assertEqual(settings.currency, "USD")

    def test_settings_delete_prevention(self):
        """Test that settings cannot be deleted."""
        settings = Settings.objects.create(locale="en_US", currency="USD")

        # Attempt to delete should not actually delete
        result = settings.delete()

        # Check that settings still exists
        self.assertTrue(Settings.objects.filter(pk=settings.pk).exists())
        # The delete method should return (0, {}) to match Django's delete signature
        self.assertEqual(result, (0, {}))

    def test_settings_unique_constraint(self):
        """Test that only one settings instance can exist."""
        Settings.objects.create(locale="en_US", currency="USD")

        # Attempting to create another should fail
        with self.assertRaises(Exception):  # Will raise IntegrityError
            Settings.objects.create(locale="fr_FR", currency="EUR")


class BudgetModelOrderingTest(TestCase):
    """Test cases for Budget model ordering."""

    def test_budget_ordering_by_name(self):
        """Test that budgets are ordered by name first."""
        # Create budgets with same created_at (within same second)
        Budget.objects.create(name="Zebra Budget", start_date=date.today())
        Budget.objects.create(name="Alpha Budget", start_date=date.today())
        Budget.objects.create(name="Beta Budget", start_date=date.today())

        budget_names = list(Budget.objects.values_list("name", flat=True))
        self.assertEqual(budget_names, ["Alpha Budget", "Beta Budget", "Zebra Budget"])

    def test_budget_ordering_by_created_at_for_same_name(self):
        """Test that budgets with same name are ordered by created_at."""
        # Create budgets with same name but different times
        budget1 = Budget.objects.create(name="Test Budget", start_date=date.today())
        # Small delay to ensure different created_at
        import time

        time.sleep(0.01)
        budget2 = Budget.objects.create(name="Test Budget", start_date=date.today())

        budgets = list(Budget.objects.filter(name="Test Budget"))
        self.assertEqual(budgets[0], budget1)
        self.assertEqual(budgets[1], budget2)


class BudgetMonthModelTest(TestCase):
    """Test cases for BudgetMonth model methods."""

    def setUp(self):
        """Set up test data."""
        self.budget = Budget.objects.create(name="Test Budget", start_date=date.today())
        self.month = BudgetMonth.objects.create(budget=self.budget, year=2024, month=1)
        self.expense = Expense.objects.create(
            budget=self.budget,
            title="Test Expense",
            expense_type="endless_recurring",
            amount=Decimal("100.00"),
            start_date=date.today(),
            day_of_month=date.today().day,
        )

    def test_has_paid_expenses_false(self):
        """Test has_paid_expenses when no paid items exist."""
        ExpenseItem.objects.create(
            expense=self.expense,
            month=self.month,
            amount=Decimal("100.00"),
            due_date=date.today(),

        )
        self.assertFalse(self.month.has_paid_expenses())

    def test_has_paid_expenses_true(self):
        """Test has_paid_expenses when paid items exist."""
        create_paid_expense_item(
            expense=self.expense,
            month=self.month,
            amount=Decimal("100.00"),
            due_date=date.today(),
        )
        self.assertTrue(self.month.has_paid_expenses())

    def test_can_be_deleted_with_no_paid_expenses(self):
        """Test can_be_deleted returns True when no paid expenses."""
        ExpenseItem.objects.create(
            expense=self.expense,
            month=self.month,
            amount=Decimal("100.00"),
            due_date=date.today(),

        )
        self.assertTrue(self.month.can_be_deleted())

    def test_can_be_deleted_with_paid_expenses(self):
        """Test can_be_deleted returns False when paid expenses exist."""
        create_paid_expense_item(
            expense=self.expense,
            month=self.month,
            amount=Decimal("100.00"),
            due_date=date.today(),
        )
        self.assertFalse(self.month.can_be_deleted())

    def test_get_most_recent_without_budget(self):
        """Test get_most_recent for all budgets."""
        # Create another month in different budget
        budget2 = Budget.objects.create(name="Budget 2", start_date=date.today())
        month2 = BudgetMonth.objects.create(budget=budget2, year=2024, month=2)

        # Most recent should be the one with latest year/month
        most_recent = BudgetMonth.get_most_recent()
        self.assertEqual(most_recent, month2)

    def test_get_most_recent_with_budget(self):
        """Test get_most_recent for specific budget."""
        # Create months in same budget
        month2 = BudgetMonth.objects.create(budget=self.budget, year=2024, month=3)

        # Create month in different budget
        budget2 = Budget.objects.create(name="Budget 2", start_date=date.today())
        BudgetMonth.objects.create(budget=budget2, year=2024, month=5)

        # Most recent for specific budget
        most_recent = BudgetMonth.get_most_recent(budget=self.budget)
        self.assertEqual(most_recent, month2)
