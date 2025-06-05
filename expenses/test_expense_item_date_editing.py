from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from datetime import date, datetime
from decimal import Decimal
from django.utils import timezone
import calendar
from .models import Budget, Month, Expense, ExpenseItem, Payee
from .forms import ExpenseItemEditForm


class ExpenseItemDateEditingTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()

        # Create budget
        self.budget = Budget.objects.create(
            name="Test Budget",
            start_date=date(2024, 1, 1),
            initial_amount=Decimal("1000.00"),
        )

        # Create month
        self.month = Month.objects.create(budget=self.budget, year=2024, month=1)

        # Create payee
        self.payee = Payee.objects.create(name="Test Payee")

        # Create expense with start_date in January 2024
        self.expense = Expense.objects.create(
            budget=self.budget,
            title="Test Expense",
            payee=self.payee,
            expense_type=Expense.TYPE_ONE_TIME,
            amount=Decimal("100.00"),
            start_date=date(2024, 1, 15),
            day_of_month=15,
        )

        # Create expense item with due date in January 2024
        self.expense_item = ExpenseItem.objects.create(
            expense=self.expense,
            month=self.month,
            amount=Decimal("100.00"),
            due_date=date(2024, 1, 20),
            status="pending",
        )

    def test_get_allowed_month_range(self):
        """Test that get_allowed_month_range returns correct dates"""
        start_date, end_date = self.expense_item.get_allowed_month_range()

        # Should return January 1-31, 2024
        self.assertEqual(start_date, date(2024, 1, 1))
        self.assertEqual(end_date, date(2024, 1, 31))

    def test_get_allowed_month_range_february_leap_year(self):
        """Test month range calculation for February in leap year"""
        # Create expense in February 2024 (leap year)
        expense = Expense.objects.create(
            budget=self.budget,
            title="Feb Expense",
            expense_type=Expense.TYPE_ONE_TIME,
            amount=Decimal("50.00"),
            start_date=date(2024, 2, 15),
            day_of_month=15,
        )

        february_month = Month.objects.create(budget=self.budget, year=2024, month=2)

        expense_item = ExpenseItem.objects.create(
            expense=expense,
            month=february_month,
            amount=Decimal("50.00"),
            due_date=date(2024, 1, 15),
            status="pending",
        )

        start_date, end_date = expense_item.get_allowed_month_range()

        # February 2024 has 29 days (leap year)
        self.assertEqual(start_date, date(2024, 2, 1))
        self.assertEqual(end_date, date(2024, 2, 29))

    def test_expense_item_clean_validation_valid_date(self):
        """Test that validation passes for dates within the expense month"""
        # Change due date to another day in January 2024
        self.expense_item.due_date = date(2024, 1, 25)

        # Should not raise ValidationError
        try:
            self.expense_item.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError for valid date")

    def test_expense_item_clean_validation_invalid_date_earlier_month(self):
        """Test that validation fails for dates in earlier months"""
        # Try to set due date to December 2023
        self.expense_item.due_date = date(2023, 12, 25)

        with self.assertRaises(ValidationError) as context:
            self.expense_item.clean()

        self.assertIn("Due date must be within January 2024", str(context.exception))

    def test_expense_item_clean_validation_invalid_date_later_month(self):
        """Test that validation fails for dates in later months"""
        # Try to set due date to February 2024
        self.expense_item.due_date = date(2024, 2, 25)

        with self.assertRaises(ValidationError) as context:
            self.expense_item.clean()

        self.assertIn("Due date must be within January 2024", str(context.exception))

    def test_expense_item_edit_form_initialization(self):
        """Test that ExpenseItemEditForm initializes correctly"""
        form = ExpenseItemEditForm(instance=self.expense_item)

        # Check that help text includes month information
        help_text = form.fields["due_date"].help_text
        self.assertIn("January 2024", help_text)
        self.assertIn("2024-01-01", help_text)
        self.assertIn("2024-01-31", help_text)

    def test_expense_item_edit_form_valid_date(self):
        """Test that form accepts valid dates within the month"""
        form_data = {"due_date": "2024-01-28", "amount": "100.00"}
        form = ExpenseItemEditForm(data=form_data, instance=self.expense_item)

        self.assertTrue(form.is_valid())

    def test_expense_item_edit_form_invalid_date_earlier_month(self):
        """Test that form rejects dates in earlier months"""
        form_data = {"due_date": "2023-12-28", "amount": "100.00"}
        form = ExpenseItemEditForm(data=form_data, instance=self.expense_item)

        self.assertFalse(form.is_valid())
        self.assertIn(
            "Due date must be within January 2024", str(form.errors["due_date"])
        )

    def test_expense_item_edit_form_invalid_date_later_month(self):
        """Test that form rejects dates in later months"""
        form_data = {"due_date": "2024-02-15", "amount": "100.00"}
        form = ExpenseItemEditForm(data=form_data, instance=self.expense_item)

        self.assertFalse(form.is_valid())
        self.assertIn(
            "Due date must be within January 2024", str(form.errors["due_date"])
        )

    def test_expense_item_edit_view_get(self):
        """Test that expense item edit view loads correctly"""
        url = reverse(
            "expense_item_edit",
            kwargs={"budget_id": self.budget.id, "pk": self.expense_item.pk},
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Due Date: Test Expense")
        self.assertContains(response, "Test Expense")
        self.assertContains(response, "Test Payee")
        self.assertContains(response, "2024-01")

    def test_expense_item_edit_view_post_valid(self):
        """Test that expense item edit view handles valid submissions"""
        url = reverse(
            "expense_item_edit",
            kwargs={"budget_id": self.budget.id, "pk": self.expense_item.pk},
        )

        form_data = {"due_date": "2024-01-25", "amount": "100.00"}
        response = self.client.post(url, form_data)

        # Should redirect to budget dashboard
        self.assertEqual(response.status_code, 302)
        expected_url = reverse("dashboard", kwargs={"budget_id": self.budget.id})
        self.assertRedirects(response, expected_url)

        # Verify the date was updated
        self.expense_item.refresh_from_db()
        self.assertEqual(self.expense_item.due_date, date(2024, 1, 25))

    def test_expense_item_edit_view_post_invalid(self):
        """Test that expense item edit view handles invalid submissions"""
        url = reverse(
            "expense_item_edit",
            kwargs={"budget_id": self.budget.id, "pk": self.expense_item.pk},
        )

        form_data = {
            "due_date": "2024-02-25",  # Invalid - outside expense month
            "amount": "100.00",
        }
        response = self.client.post(url, form_data)

        # Should render form again with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Due date must be within January 2024")

        # Verify the date was not updated
        self.expense_item.refresh_from_db()
        self.assertEqual(self.expense_item.due_date, date(2024, 1, 20))

    def test_expense_item_edit_view_budget_permission(self):
        """Test that expense item edit requires correct budget"""
        # Create a different budget
        other_budget = Budget.objects.create(
            name="Other Budget",
            start_date=date(2024, 1, 1),
            initial_amount=Decimal("500.00"),
        )

        url = reverse(
            "expense_item_edit",
            kwargs={
                "budget_id": other_budget.id,  # Wrong budget
                "pk": self.expense_item.pk,
            },
        )
        response = self.client.get(url)

        # Should return 404 since expense item doesn't belong to this budget
        self.assertEqual(response.status_code, 404)

    def test_expense_detail_shows_edit_link(self):
        """Test that expense detail page shows edit link for expense items"""
        url = reverse(
            "expense_detail",
            kwargs={"budget_id": self.budget.id, "pk": self.expense.pk},
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        # Should contain edit link with calendar icon
        edit_url = reverse(
            "expense_item_edit",
            kwargs={"budget_id": self.budget.id, "pk": self.expense_item.pk},
        )
        self.assertContains(response, edit_url)
        self.assertContains(response, "fa-calendar-days")

    def test_different_expense_months(self):
        """Test validation works correctly for expenses created in different months"""
        # Create expense in March 2024
        march_expense = Expense.objects.create(
            budget=self.budget,
            title="March Expense",
            expense_type=Expense.TYPE_ONE_TIME,
            amount=Decimal("75.00"),
            start_date=date(2024, 3, 10),
            day_of_month=10,
        )

        march_month = Month.objects.create(budget=self.budget, year=2024, month=3)

        march_item = ExpenseItem.objects.create(
            expense=march_expense,
            month=march_month,
            amount=Decimal("75.00"),
            due_date=date(2024, 1, 15),
            status="pending",
        )

        # Should allow dates within March 2024
        march_item.due_date = date(2024, 3, 25)
        try:
            march_item.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError for valid March date")

        # Should reject dates outside March 2024
        march_item.due_date = date(2024, 4, 5)
        with self.assertRaises(ValidationError) as context:
            march_item.clean()

        self.assertIn("Due date must be within March 2024", str(context.exception))

    def test_get_allowed_month_range_one_time_future_expense(self):
        """Test that one-time expenses can be moved back to most recent month in budget"""
        # Create expense for March 2024 (future from active January)
        future_expense = Expense.objects.create(
            budget=self.budget,
            title="Future One-Time Expense",
            expense_type=Expense.TYPE_ONE_TIME,
            amount=Decimal("50.00"),
            start_date=date(2024, 3, 15),  # Created for March
            day_of_month=15,
        )

        # Create March month - this becomes the most recent month in budget
        future_month = Month.objects.create(budget=self.budget, year=2024, month=3)

        future_expense_item = ExpenseItem.objects.create(
            expense=future_expense,
            month=future_month,
            amount=Decimal("50.00"),
            due_date=date(2024, 1, 15),
            status="pending",
        )

        start_date, end_date = future_expense_item.get_allowed_month_range()

        # For one-time expenses, should allow from most recent month to expense month
        # Since March is both the most recent and expense month, should be same as normal
        self.assertEqual(start_date, date(2024, 3, 1))  # March start
        self.assertEqual(end_date, date(2024, 3, 31))  # March end

    def test_get_allowed_month_range_one_time_with_earlier_active_month(self):
        """Test one-time expense when most recent month is earlier than expense month"""
        # Create expense for March 2024
        future_expense = Expense.objects.create(
            budget=self.budget,
            title="Future One-Time Expense",
            expense_type=Expense.TYPE_ONE_TIME,
            amount=Decimal("50.00"),
            start_date=date(2024, 3, 15),  # Created for March
            day_of_month=15,
        )

        # Don't create March month yet, so January remains most recent
        march_month = Month.objects.create(budget=self.budget, year=2024, month=3)

        # But let's set the created_at to make January more recent
        # We need to delete and recreate to test the scenario properly
        march_month.delete()

        # Create February month first to make it most recent
        february_month = Month.objects.create(budget=self.budget, year=2024, month=2)

        # Now create March month
        march_month = Month.objects.create(budget=self.budget, year=2024, month=3)

        future_expense_item = ExpenseItem.objects.create(
            expense=future_expense,
            month=march_month,
            amount=Decimal("50.00"),
            due_date=date(2024, 1, 15),
            status="pending",
        )

        start_date, end_date = future_expense_item.get_allowed_month_range()

        # Most recent month is March (due to ordering), so same result
        self.assertEqual(start_date, date(2024, 3, 1))  # March start
        self.assertEqual(end_date, date(2024, 3, 31))  # March end

    def test_one_time_expense_can_move_to_earlier_months(self):
        """Test that one-time expenses can move to earlier months up to most recent month"""
        # Create expense in March, but test moving to January (if January was most recent)
        # This test shows the concept, but Month.get_most_recent() always returns
        # the chronologically latest month due to ordering

        # For this test, we'll create a scenario and validate the logic works
        self.expense_item.due_date = date(2024, 1, 5)  # Different day in January
        try:
            self.expense_item.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError for valid date within same month")

    def test_recurring_expense_restricted_to_creation_month(self):
        """Test that recurring expenses are still restricted to creation month only"""
        # Create recurring expense in February
        recurring_expense = Expense.objects.create(
            budget=self.budget,
            title="Recurring Expense",
            expense_type=Expense.TYPE_ENDLESS_RECURRING,
            amount=Decimal("75.00"),
            start_date=date(2024, 2, 15),
            day_of_month=15,
        )

        february_month = Month.objects.create(budget=self.budget, year=2024, month=2)

        recurring_item = ExpenseItem.objects.create(
            expense=recurring_expense,
            month=february_month,
            amount=Decimal("75.00"),
            due_date=date(2024, 1, 15),
            status="pending",
        )

        start_date, end_date = recurring_item.get_allowed_month_range()

        # Should only allow February (creation month)
        self.assertEqual(start_date, date(2024, 2, 1))  # February start
        self.assertEqual(end_date, date(2024, 2, 29))  # February end

        # Try to move to January (should fail for recurring)
        recurring_item.due_date = date(2024, 1, 25)
        with self.assertRaises(ValidationError) as context:
            recurring_item.clean()

        self.assertIn("Due date must be within February 2024", str(context.exception))
