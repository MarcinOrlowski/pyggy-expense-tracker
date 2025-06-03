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
            title="One Time Expense",
            payee=self.payee,
            expense_type=Expense.TYPE_ONE_TIME,
            total_amount=Decimal("100.00"),
            started_at=date.today()
        )
        
        # Create unpaid expense item
        ExpenseItem.objects.create(
            expense=expense,
            month=self.month,
            due_date=date.today(),
            amount=Decimal("100.00"),
            status='pending'
        )
        
        self.assertTrue(expense.can_be_edited())
        self.assertTrue(expense.can_edit_amount())
        
    def test_cannot_edit_one_time_paid_expense_amount(self):
        """Test that amount cannot be edited for paid one-time expenses"""
        expense = Expense.objects.create(
            title="One Time Expense",
            payee=self.payee,
            expense_type=Expense.TYPE_ONE_TIME,
            total_amount=Decimal("100.00"),
            started_at=date.today()
        )
        
        # Create paid expense item
        ExpenseItem.objects.create(
            expense=expense,
            month=self.month,
            due_date=date.today(),
            amount=Decimal("100.00"),
            status='paid',
            payment_date=timezone.now()
        )
        
        self.assertTrue(expense.can_be_edited())  # Can still edit other fields
        self.assertFalse(expense.can_edit_amount())  # But not amount
        
    def test_can_edit_endless_recurring_unpaid_expense(self):
        """Test that endless recurring unpaid expenses can be edited"""
        expense = Expense.objects.create(
            title="Endless Recurring",
            payee=self.payee,
            expense_type=Expense.TYPE_ENDLESS_RECURRING,
            total_amount=Decimal("50.00"),
            started_at=date.today()
        )
        
        # Create unpaid expense item
        ExpenseItem.objects.create(
            expense=expense,
            month=self.month,
            due_date=date.today(),
            amount=Decimal("50.00"),
            status='pending'
        )
        
        self.assertTrue(expense.can_be_edited())
        self.assertTrue(expense.can_edit_amount())
        
    def test_cannot_edit_split_payment_expense(self):
        """Test that split payment expenses cannot be edited"""
        expense = Expense.objects.create(
            title="Split Payment",
            payee=self.payee,
            expense_type=Expense.TYPE_SPLIT_PAYMENT,
            total_amount=Decimal("100.00"),
            installments_count=3,
            started_at=date.today()
        )
        
        self.assertFalse(expense.can_be_edited())
        self.assertFalse(expense.can_edit_amount())
        
        restrictions = expense.get_edit_restrictions()
        self.assertIn('Split payment expenses cannot be edited', restrictions['reasons'])
        
    def test_cannot_edit_recurring_with_end_date_expense(self):
        """Test that recurring with end date expenses cannot be edited"""
        expense = Expense.objects.create(
            title="Recurring with End",
            payee=self.payee,
            expense_type=Expense.TYPE_RECURRING_WITH_END,
            total_amount=Decimal("75.00"),
            started_at=date.today(),
            end_date=date(date.today().year, 12, 31)
        )
        
        self.assertFalse(expense.can_be_edited())
        self.assertFalse(expense.can_edit_amount())
        
        restrictions = expense.get_edit_restrictions()
        self.assertIn('Recurring expenses with end date cannot be edited', restrictions['reasons'])
        
    def test_cannot_edit_closed_expense(self):
        """Test that closed expenses cannot be edited"""
        expense = Expense.objects.create(
            title="Closed Expense",
            payee=self.payee,
            expense_type=Expense.TYPE_ONE_TIME,
            total_amount=Decimal("100.00"),
            started_at=date.today(),
            closed_at=timezone.now()
        )
        
        self.assertFalse(expense.can_be_edited())
        self.assertFalse(expense.can_edit_amount())
        
        restrictions = expense.get_edit_restrictions()
        self.assertIn('Expense is closed', restrictions['reasons'])
        
    def test_get_edit_restrictions_multiple_reasons(self):
        """Test get_edit_restrictions returns all applicable reasons"""
        expense = Expense.objects.create(
            title="Endless Recurring",
            payee=self.payee,
            expense_type=Expense.TYPE_ENDLESS_RECURRING,
            total_amount=Decimal("50.00"),
            started_at=date.today()
        )
        
        # Create paid expense item
        ExpenseItem.objects.create(
            expense=expense,
            month=self.month,
            due_date=date.today(),
            amount=Decimal("50.00"),
            status='paid',
            payment_date=timezone.now()
        )
        
        restrictions = expense.get_edit_restrictions()
        self.assertTrue(restrictions['can_edit'])
        self.assertFalse(restrictions['can_edit_amount'])
        self.assertIn('Amount cannot be edited because expense has paid items', restrictions['reasons'])
        
    def test_expense_edit_view_redirects_for_non_editable(self):
        """Test that edit view redirects with error for non-editable expenses"""
        expense = Expense.objects.create(
            title="Split Payment",
            payee=self.payee,
            expense_type=Expense.TYPE_SPLIT_PAYMENT,
            total_amount=Decimal("100.00"),
            installments_count=3,
            started_at=date.today()
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
            title="One Time Expense",
            payee=self.payee,
            expense_type=Expense.TYPE_ONE_TIME,
            total_amount=Decimal("100.00"),
            started_at=date.today()
        )
        
        # Create paid expense item
        ExpenseItem.objects.create(
            expense=expense,
            month=self.month,
            due_date=date.today(),
            amount=Decimal("100.00"),
            status='paid',
            payment_date=timezone.now()
        )
        
        # Try to change amount via POST
        url = reverse('expense_edit', kwargs={'budget_id': self.budget.id, 'pk': expense.pk})
        post_data = {
            'title': 'Updated Title',
            'expense_type': Expense.TYPE_ONE_TIME,
            'total_amount': '200.00',  # Try to change amount
            'started_at': date.today().strftime('%Y-%m-%d'),
            'installments_count': '0',
            'notes': 'Updated notes'
        }
        
        response = self.client.post(url, post_data)
        
        # Should redirect successfully because disabled fields are not sent in POST
        # The form will use the original value for disabled fields
        self.assertEqual(response.status_code, 302)
        
        # Verify amount wasn't changed (disabled field preserves original value)
        expense.refresh_from_db()
        self.assertEqual(expense.total_amount, Decimal("100.00"))
        self.assertEqual(expense.title, 'Updated Title')  # But other fields are updated
        
    def test_expense_detail_shows_disabled_edit_button(self):
        """Test that expense detail shows disabled edit button with tooltip"""
        expense = Expense.objects.create(
            title="Split Payment",
            payee=self.payee,
            expense_type=Expense.TYPE_SPLIT_PAYMENT,
            total_amount=Decimal("100.00"),
            installments_count=3,
            started_at=date.today()
        )
        
        url = reverse('expense_detail', kwargs={'budget_id': self.budget.id, 'pk': expense.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'disabled')
        self.assertContains(response, 'Split payment expenses cannot be edited')