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
            initial_amount=Decimal("1000.00")
        )
        
        # Create month
        self.month = Month.objects.create(
            budget=self.budget,
            year=2024,
            month=1
        )
        
        # Create payee
        self.payee = Payee.objects.create(name="Test Payee")
        
        # Create expense with started_at in January 2024
        self.expense = Expense.objects.create(
            budget=self.budget,
            title="Test Expense",
            payee=self.payee,
            expense_type=Expense.TYPE_ONE_TIME,
            total_amount=Decimal("100.00"),
            started_at=date(2024, 1, 15)
        )
        
        # Create expense item with due date in January 2024
        self.expense_item = ExpenseItem.objects.create(
            expense=self.expense,
            month=self.month,
            due_date=date(2024, 1, 20),
            amount=Decimal("100.00"),
            status='pending'
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
            total_amount=Decimal("50.00"),
            started_at=date(2024, 2, 15)
        )
        
        february_month = Month.objects.create(
            budget=self.budget,
            year=2024,
            month=2
        )
        
        expense_item = ExpenseItem.objects.create(
            expense=expense,
            month=february_month,
            due_date=date(2024, 2, 20),
            amount=Decimal("50.00"),
            status='pending'
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
        
        self.assertIn('Due date must be within January 2024', str(context.exception))

    def test_expense_item_clean_validation_invalid_date_later_month(self):
        """Test that validation fails for dates in later months"""
        # Try to set due date to February 2024
        self.expense_item.due_date = date(2024, 2, 25)
        
        with self.assertRaises(ValidationError) as context:
            self.expense_item.clean()
        
        self.assertIn('Due date must be within January 2024', str(context.exception))

    def test_expense_item_edit_form_initialization(self):
        """Test that ExpenseItemEditForm initializes correctly"""
        form = ExpenseItemEditForm(instance=self.expense_item)
        
        # Check that help text includes month information
        help_text = form.fields['due_date'].help_text
        self.assertIn('January 2024', help_text)
        self.assertIn('2024-01-01', help_text)
        self.assertIn('2024-01-31', help_text)

    def test_expense_item_edit_form_valid_date(self):
        """Test that form accepts valid dates within the month"""
        form_data = {
            'due_date': '2024-01-28'
        }
        form = ExpenseItemEditForm(data=form_data, instance=self.expense_item)
        
        self.assertTrue(form.is_valid())

    def test_expense_item_edit_form_invalid_date_earlier_month(self):
        """Test that form rejects dates in earlier months"""
        form_data = {
            'due_date': '2023-12-28'
        }
        form = ExpenseItemEditForm(data=form_data, instance=self.expense_item)
        
        self.assertFalse(form.is_valid())
        self.assertIn('Due date must be within January 2024', str(form.errors['due_date']))

    def test_expense_item_edit_form_invalid_date_later_month(self):
        """Test that form rejects dates in later months"""
        form_data = {
            'due_date': '2024-02-15'
        }
        form = ExpenseItemEditForm(data=form_data, instance=self.expense_item)
        
        self.assertFalse(form.is_valid())
        self.assertIn('Due date must be within January 2024', str(form.errors['due_date']))

    def test_expense_item_edit_view_get(self):
        """Test that expense item edit view loads correctly"""
        url = reverse('expense_item_edit', kwargs={
            'budget_id': self.budget.id,
            'pk': self.expense_item.pk
        })
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Due Date: Test Expense')
        self.assertContains(response, 'Test Expense')
        self.assertContains(response, 'Test Payee')
        self.assertContains(response, '2024-01')

    def test_expense_item_edit_view_post_valid(self):
        """Test that expense item edit view handles valid submissions"""
        url = reverse('expense_item_edit', kwargs={
            'budget_id': self.budget.id,
            'pk': self.expense_item.pk
        })
        
        form_data = {
            'due_date': '2024-01-25'
        }
        response = self.client.post(url, form_data)
        
        # Should redirect to expense detail
        self.assertEqual(response.status_code, 302)
        expected_url = reverse('expense_detail', kwargs={
            'budget_id': self.budget.id,
            'pk': self.expense.pk
        })
        self.assertRedirects(response, expected_url)
        
        # Verify the date was updated
        self.expense_item.refresh_from_db()
        self.assertEqual(self.expense_item.due_date, date(2024, 1, 25))

    def test_expense_item_edit_view_post_invalid(self):
        """Test that expense item edit view handles invalid submissions"""
        url = reverse('expense_item_edit', kwargs={
            'budget_id': self.budget.id,
            'pk': self.expense_item.pk
        })
        
        form_data = {
            'due_date': '2024-02-25'  # Invalid - outside expense month
        }
        response = self.client.post(url, form_data)
        
        # Should render form again with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Due date must be within January 2024')
        
        # Verify the date was not updated
        self.expense_item.refresh_from_db()
        self.assertEqual(self.expense_item.due_date, date(2024, 1, 20))

    def test_expense_item_edit_view_budget_permission(self):
        """Test that expense item edit requires correct budget"""
        # Create a different budget
        other_budget = Budget.objects.create(
            name="Other Budget",
            start_date=date(2024, 1, 1),
            initial_amount=Decimal("500.00")
        )
        
        url = reverse('expense_item_edit', kwargs={
            'budget_id': other_budget.id,  # Wrong budget
            'pk': self.expense_item.pk
        })
        response = self.client.get(url)
        
        # Should return 404 since expense item doesn't belong to this budget
        self.assertEqual(response.status_code, 404)

    def test_expense_detail_shows_edit_link(self):
        """Test that expense detail page shows edit link for expense items"""
        url = reverse('expense_detail', kwargs={
            'budget_id': self.budget.id,
            'pk': self.expense.pk
        })
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Should contain edit link with calendar icon
        edit_url = reverse('expense_item_edit', kwargs={
            'budget_id': self.budget.id,
            'pk': self.expense_item.pk
        })
        self.assertContains(response, edit_url)
        self.assertContains(response, 'fa-calendar-days')

    def test_different_expense_months(self):
        """Test validation works correctly for expenses created in different months"""
        # Create expense in March 2024
        march_expense = Expense.objects.create(
            budget=self.budget,
            title="March Expense",
            expense_type=Expense.TYPE_ONE_TIME,
            total_amount=Decimal("75.00"),
            started_at=date(2024, 3, 10)
        )
        
        march_month = Month.objects.create(
            budget=self.budget,
            year=2024,
            month=3
        )
        
        march_item = ExpenseItem.objects.create(
            expense=march_expense,
            month=march_month,
            due_date=date(2024, 3, 15),
            amount=Decimal("75.00"),
            status='pending'
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
        
        self.assertIn('Due date must be within March 2024', str(context.exception))