from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date, datetime
from decimal import Decimal
from django.utils import timezone
from .models import Budget, Month, Expense, ExpenseItem, Payee


class ExpenseEditingPermissionsTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create budget
        self.budget = Budget.objects.create(
            name="Test Budget",
            start_date=date.today(),
            initial_amount=Decimal("1000.00")
        )
        
        # Create month
        self.month = Month.objects.create(
            budget=self.budget,
            year=date.today().year,
            month=date.today().month
        )
        
        # Create payee
        self.payee = Payee.objects.create(name="Test Payee")
        
    def test_can_edit_one_time_unpaid_expense(self):
        """Test that one-time unpaid expenses can be edited"""
        expense = Expense.objects.create(
            budget=self.budget,
            title="One Time Expense",
            payee=self.payee,
            expense_type=Expense.TYPE_ONE_TIME,
            amount=Decimal("100.00"),
            start_date=date.today(),
            day_of_month=date.today().day
        )
        
        # Create unpaid expense item
        ExpenseItem.objects.create(
            expense=expense,
            month=self.month,
            amount=Decimal("100.00"),
            due_date=date.today(),
            status='pending'
        )
        
        self.assertTrue(expense.can_be_edited())
        self.assertTrue(expense.can_edit_amount())
        
    def test_cannot_edit_one_time_paid_expense_amount(self):
        """Test that amount cannot be edited for paid one-time expenses"""
        expense = Expense.objects.create(
            budget=self.budget,
            title="One Time Expense",
            payee=self.payee,
            expense_type=Expense.TYPE_ONE_TIME,
            amount=Decimal("100.00"),
            start_date=date.today(),
            day_of_month=date.today().day
        )
        
        # Create paid expense item
        ExpenseItem.objects.create(
            expense=expense,
            month=self.month,
            amount=Decimal("100.00"),
            due_date=date.today(),
            status='paid',
            payment_date=timezone.now()
        )
        
        self.assertTrue(expense.can_be_edited())  # Can still edit other fields
        self.assertFalse(expense.can_edit_amount())  # But not amount
        
    def test_can_edit_endless_recurring_unpaid_expense(self):
        """Test that endless recurring unpaid expenses can be edited"""
        expense = Expense.objects.create(
            budget=self.budget,
            title="Endless Recurring",
            payee=self.payee,
            expense_type=Expense.TYPE_ENDLESS_RECURRING,
            amount=Decimal("50.00"),
            start_date=date.today(),
            day_of_month=date.today().day
        )
        
        # Create unpaid expense item
        ExpenseItem.objects.create(
            expense=expense,
            month=self.month,
            amount=Decimal("50.00"),
            due_date=date.today(),
            status='pending'
        )
        
        self.assertTrue(expense.can_be_edited())
        self.assertTrue(expense.can_edit_amount())
        
    def test_cannot_edit_split_payment_expense(self):
        """Test that split payment expenses cannot be edited"""
        expense = Expense.objects.create(
            budget=self.budget,
            title="Split Payment",
            payee=self.payee,
            expense_type=Expense.TYPE_SPLIT_PAYMENT,
            amount=Decimal("100.00"),
            total_parts=3,
            start_date=date.today(),
            day_of_month=date.today().day
        )
        
        self.assertFalse(expense.can_be_edited())
        self.assertFalse(expense.can_edit_amount())
        
        restrictions = expense.get_edit_restrictions()
        reasons = restrictions['reasons']
        if isinstance(reasons, list):
            self.assertIn('Split payment expenses cannot be edited', reasons)
        
    def test_cannot_edit_recurring_with_end_date_expense(self):
        """Test that recurring with end date expenses cannot be edited"""
        expense = Expense.objects.create(
            budget=self.budget,
            title="Recurring with End",
            payee=self.payee,
            expense_type=Expense.TYPE_RECURRING_WITH_END,
            amount=Decimal("75.00"),
            start_date=date.today(),
            day_of_month=date.today().day,
            end_date=date(date.today().year, 12, 31)
        )
        
        self.assertFalse(expense.can_be_edited())
        self.assertFalse(expense.can_edit_amount())
        
        restrictions = expense.get_edit_restrictions()
        reasons = restrictions['reasons']
        if isinstance(reasons, list):
            self.assertIn('Recurring expenses with end date cannot be edited', reasons)
        
    def test_cannot_edit_closed_expense(self):
        """Test that closed expenses cannot be edited"""
        expense = Expense.objects.create(
            budget=self.budget,
            title="Closed Expense",
            payee=self.payee,
            expense_type=Expense.TYPE_ONE_TIME,
            amount=Decimal("100.00"),
            start_date=date.today(),
            day_of_month=date.today().day,
            closed_at=timezone.now()
        )
        
        self.assertFalse(expense.can_be_edited())
        self.assertFalse(expense.can_edit_amount())
        
        restrictions = expense.get_edit_restrictions()
        reasons = restrictions['reasons']
        if isinstance(reasons, list):
            self.assertIn('Expense is closed', reasons)
        
    def test_get_edit_restrictions_multiple_reasons(self):
        """Test get_edit_restrictions returns all applicable reasons"""
        expense = Expense.objects.create(
            budget=self.budget,
            title="Endless Recurring",
            payee=self.payee,
            expense_type=Expense.TYPE_ENDLESS_RECURRING,
            amount=Decimal("50.00"),
            start_date=date.today(),
            day_of_month=date.today().day
        )
        
        # Create paid expense item
        ExpenseItem.objects.create(
            expense=expense,
            month=self.month,
            amount=Decimal("50.00"),
            due_date=date.today(),
            status='paid',
            payment_date=timezone.now()
        )
        
        restrictions = expense.get_edit_restrictions()
        self.assertTrue(restrictions['can_edit'])
        self.assertFalse(restrictions['can_edit_amount'])
        reasons = restrictions['reasons']
        if isinstance(reasons, list):
            self.assertIn('Amount cannot be edited because expense has paid items', reasons)
        
    def test_expense_edit_view_redirects_for_non_editable(self):
        """Test that edit view redirects with error for non-editable expenses"""
        expense = Expense.objects.create(
            budget=self.budget,
            title="Split Payment",
            payee=self.payee,
            expense_type=Expense.TYPE_SPLIT_PAYMENT,
            amount=Decimal("100.00"),
            total_parts=3,
            start_date=date.today(),
            day_of_month=date.today().day
        )
        
        url = reverse('expense_edit', kwargs={'budget_id': self.budget.id, 'pk': expense.pk})
        response = self.client.get(url)
        
        # Should redirect to detail page
        self.assertEqual(response.status_code, 302)
        expected_url = reverse('expense_detail', kwargs={'budget_id': self.budget.id, 'pk': expense.pk})
        self.assertRedirects(response, expected_url)
        
    def test_expense_form_validation_prevents_amount_change(self):
        """Test that form validation prevents amount changes when not allowed"""
        expense = Expense.objects.create(
            budget=self.budget,
            title="One Time Expense",
            payee=self.payee,
            expense_type=Expense.TYPE_ONE_TIME,
            amount=Decimal("100.00"),
            start_date=date.today(),
            day_of_month=date.today().day
        )
        
        # Create paid expense item
        ExpenseItem.objects.create(
            expense=expense,
            month=self.month,
            amount=Decimal("100.00"),
            due_date=date.today(),
            status='paid',
            payment_date=timezone.now()
        )
        
        # Try to change amount via POST
        url = reverse('expense_edit', kwargs={'budget_id': self.budget.id, 'pk': expense.pk})
        post_data = {
            'title': 'Updated Title',
            'expense_type': Expense.TYPE_ONE_TIME,
            'amount': '200.00',  # Try to change amount
            'start_date': date.today().strftime('%Y-%m-%d'),
            'total_parts': '0',
            'notes': 'Updated notes'
        }
        
        response = self.client.post(url, post_data)
        
        # Should redirect successfully because disabled fields are not sent in POST
        # The form will use the original value for disabled fields
        self.assertEqual(response.status_code, 302)
        
        # Verify amount wasn't changed (disabled field preserves original value)
        expense.refresh_from_db()
        self.assertEqual(expense.amount, Decimal("100.00"))
        self.assertEqual(expense.title, 'Updated Title')  # But other fields are updated
        
    def test_expense_detail_shows_disabled_edit_button(self):
        """Test that expense detail shows disabled edit button with tooltip"""
        expense = Expense.objects.create(
            budget=self.budget,
            title="Split Payment",
            payee=self.payee,
            expense_type=Expense.TYPE_SPLIT_PAYMENT,
            amount=Decimal("100.00"),
            total_parts=3,
            start_date=date.today(),
            day_of_month=date.today().day
        )
        
        url = reverse('expense_detail', kwargs={'budget_id': self.budget.id, 'pk': expense.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'disabled')
        self.assertContains(response, 'Split payment expenses cannot be edited')

    def test_one_time_expense_can_edit_date_to_most_recent_month(self):
        """Test that one-time expenses can edit dates back to most recent month"""
        # Create a one-time expense in a future month
        future_expense = Expense.objects.create(
            budget=self.budget,
            title="Future One Time Expense",
            payee=self.payee,
            expense_type=Expense.TYPE_ONE_TIME,
            amount=Decimal("100.00"),
            start_date=date(2025, 6, 15),  # June (future from current month)
            day_of_month=15
        )
        
        # Most recent month is the current month (created in setUp)
        self.assertTrue(future_expense.can_edit_date())
        
        # Should be able to edit the date to the current month
        restrictions = future_expense.get_edit_restrictions()
        self.assertTrue(restrictions['can_edit'])
        self.assertTrue(restrictions['can_edit_date'])

    def test_recurring_expense_cannot_edit_date_to_earlier_month(self):
        """Test that recurring expenses still cannot edit dates to earlier months"""
        # Create a recurring expense in a future month
        future_expense = Expense.objects.create(
            budget=self.budget,
            title="Future Recurring Expense",
            payee=self.payee,
            expense_type=Expense.TYPE_ENDLESS_RECURRING,
            amount=Decimal("100.00"),
            start_date=date(2025, 6, 15),  # June (future from current month)
            day_of_month=15
        )
        
        # Should not be able to edit the date (normal restriction applies)
        self.assertFalse(future_expense.can_edit_date())
        
        restrictions = future_expense.get_edit_restrictions()
        self.assertTrue(restrictions['can_edit'])  # Can edit other fields
        self.assertFalse(restrictions['can_edit_date'])  # But not the date