from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date, timedelta
from .models import Budget, BudgetMonth, Expense, ExpenseItem, Payment, PaymentMethod, Payee


class ExpenseItemDeletionTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")
        
        # Create test budget
        self.budget = Budget.objects.create(
            name="Test Budget",
            start_date=date.today(),
            initial_amount=Decimal("1000.00")
        )
        
        # Create test month
        current_date = date.today()
        self.current_month = BudgetMonth.objects.create(
            budget=self.budget,
            year=current_date.year,
            month=current_date.month
        )
        
        # Create past month for testing
        past_date = current_date - timedelta(days=32)
        self.past_month = BudgetMonth.objects.create(
            budget=self.budget,
            year=past_date.year,
            month=past_date.month
        )
        
        # Create payment method and payee
        self.payment_method = PaymentMethod.objects.create(
            name="Test Payment Method"
        )
        
        self.payee = Payee.objects.create(name="Test Payee")

    def test_can_be_deleted_method_returns_true_for_valid_conditions(self):
        """Test can_be_deleted() returns True for unpaid one-time expense from current month"""
        # Create one-time expense
        expense = Expense.objects.create(
            title="Test One-time Expense",
            amount=Decimal("100.00"),
            expense_type=Expense.TYPE_ONE_TIME,
            start_date=date.today(),
            day_of_month=date.today().day,
            budget=self.budget,
            payee=self.payee
        )
        
        # Create expense item in current month
        expense_item = ExpenseItem.objects.create(
            expense=expense,
            month=self.current_month,
            due_date=date.today(),
            amount=Decimal("100.00")
        )
        
        self.assertTrue(expense_item.can_be_deleted())

    def test_can_be_deleted_method_returns_false_for_paid_item(self):
        """Test can_be_deleted() returns False when expense item has payment records"""
        # Create one-time expense
        expense = Expense.objects.create(
            title="Test One-time Expense",
            amount=Decimal("100.00"),
            expense_type=Expense.TYPE_ONE_TIME,
            start_date=date.today(),
            day_of_month=date.today().day,
            budget=self.budget,
            payee=self.payee
        )
        
        # Create expense item in current month
        expense_item = ExpenseItem.objects.create(
            expense=expense,
            month=self.current_month,
            due_date=date.today(),
            amount=Decimal("100.00")
        )
        
        # Add payment record
        Payment.objects.create(
            expense_item=expense_item,
            amount=Decimal("50.00"),
            payment_date=date.today(),
            payment_method=self.payment_method
        )
        
        self.assertFalse(expense_item.can_be_deleted())

    def test_can_be_deleted_method_returns_false_for_recurring_expense(self):
        """Test can_be_deleted() returns False for recurring expense types"""
        # Create recurring expense
        expense = Expense.objects.create(
            title="Test Recurring Expense",
            amount=Decimal("100.00"),
            expense_type=Expense.TYPE_ENDLESS_RECURRING,
            start_date=date.today(),
            day_of_month=date.today().day,
            budget=self.budget,
            payee=self.payee
        )
        
        # Create expense item in current month
        expense_item = ExpenseItem.objects.create(
            expense=expense,
            month=self.current_month,
            due_date=date.today(),
            amount=Decimal("100.00")
        )
        
        self.assertFalse(expense_item.can_be_deleted())

    def test_can_be_deleted_method_returns_false_for_past_month(self):
        """Test can_be_deleted() returns False for items from past months"""
        # Create one-time expense
        expense = Expense.objects.create(
            title="Test One-time Expense",
            amount=Decimal("100.00"),
            expense_type=Expense.TYPE_ONE_TIME,
            start_date=date.today(),
            day_of_month=date.today().day,
            budget=self.budget,
            payee=self.payee
        )
        
        # Create expense item in past month
        expense_item = ExpenseItem.objects.create(
            expense=expense,
            month=self.past_month,
            due_date=date.today() - timedelta(days=32),
            amount=Decimal("100.00")
        )
        
        self.assertFalse(expense_item.can_be_deleted())

    def test_delete_view_redirects_when_item_cannot_be_deleted(self):
        """Test that delete view redirects with error when item cannot be deleted"""
        # Create recurring expense (cannot be deleted)
        expense = Expense.objects.create(
            title="Test Recurring Expense",
            amount=Decimal("100.00"),
            expense_type=Expense.TYPE_ENDLESS_RECURRING,
            start_date=date.today(),
            day_of_month=date.today().day,
            budget=self.budget,
            payee=self.payee
        )
        
        expense_item = ExpenseItem.objects.create(
            expense=expense,
            month=self.current_month,
            due_date=date.today(),
            amount=Decimal("100.00")
        )
        
        url = reverse("expense_item_delete", kwargs={"budget_id": self.budget.id, "pk": expense_item.pk})
        response = self.client.get(url)
        
        # Should redirect to dashboard
        self.assertRedirects(response, reverse("dashboard", kwargs={"budget_id": self.budget.id}))

    def test_delete_view_shows_confirmation_page_for_valid_item(self):
        """Test that delete view shows confirmation page for deletable items"""
        # Create one-time expense
        expense = Expense.objects.create(
            title="Test One-time Expense",
            amount=Decimal("100.00"),
            expense_type=Expense.TYPE_ONE_TIME,
            start_date=date.today(),
            day_of_month=date.today().day,
            budget=self.budget,
            payee=self.payee
        )
        
        expense_item = ExpenseItem.objects.create(
            expense=expense,
            month=self.current_month,
            due_date=date.today(),
            amount=Decimal("100.00")
        )
        
        url = reverse("expense_item_delete", kwargs={"budget_id": self.budget.id, "pk": expense_item.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Confirm Deletion")
        self.assertContains(response, expense.title)

    def test_delete_view_post_deletes_expense_and_item(self):
        """Test that POST to delete view deletes both expense item and parent expense"""
        # Create one-time expense
        expense = Expense.objects.create(
            title="Test One-time Expense",
            amount=Decimal("100.00"),
            expense_type=Expense.TYPE_ONE_TIME,
            start_date=date.today(),
            day_of_month=date.today().day,
            budget=self.budget,
            payee=self.payee
        )
        
        expense_item = ExpenseItem.objects.create(
            expense=expense,
            month=self.current_month,
            due_date=date.today(),
            amount=Decimal("100.00")
        )
        
        expense_id = expense.id
        expense_item_id = expense_item.id
        
        url = reverse("expense_item_delete", kwargs={"budget_id": self.budget.id, "pk": expense_item.pk})
        response = self.client.post(url)
        
        # Should redirect to dashboard
        self.assertRedirects(response, reverse("dashboard", kwargs={"budget_id": self.budget.id}))
        
        # Both expense and expense item should be deleted
        self.assertFalse(Expense.objects.filter(id=expense_id).exists())
        self.assertFalse(ExpenseItem.objects.filter(id=expense_item_id).exists())

    def test_delete_view_post_blocks_deletion_when_invalid(self):
        """Test that POST to delete view blocks deletion when item cannot be deleted"""
        # Create recurring expense (cannot be deleted)
        expense = Expense.objects.create(
            title="Test Recurring Expense",
            amount=Decimal("100.00"),
            expense_type=Expense.TYPE_ENDLESS_RECURRING,
            start_date=date.today(),
            day_of_month=date.today().day,
            budget=self.budget,
            payee=self.payee
        )
        
        expense_item = ExpenseItem.objects.create(
            expense=expense,
            month=self.current_month,
            due_date=date.today(),
            amount=Decimal("100.00")
        )
        
        expense_id = expense.id
        expense_item_id = expense_item.id
        
        url = reverse("expense_item_delete", kwargs={"budget_id": self.budget.id, "pk": expense_item.pk})
        response = self.client.post(url)
        
        # Should redirect to dashboard
        self.assertRedirects(response, reverse("dashboard", kwargs={"budget_id": self.budget.id}))
        
        # Both expense and expense item should still exist
        self.assertTrue(Expense.objects.filter(id=expense_id).exists())
        self.assertTrue(ExpenseItem.objects.filter(id=expense_item_id).exists())

    def test_delete_button_appears_for_deletable_items(self):
        """Test that delete button appears in UI for deletable items"""
        # Create one-time expense
        expense = Expense.objects.create(
            title="Test One-time Expense",
            amount=Decimal("100.00"),
            expense_type=Expense.TYPE_ONE_TIME,
            start_date=date.today(),
            day_of_month=date.today().day,
            budget=self.budget,
            payee=self.payee
        )
        
        expense_item = ExpenseItem.objects.create(
            expense=expense,
            month=self.current_month,
            due_date=date.today(),
            amount=Decimal("100.00")
        )
        
        # Check dashboard to see if delete button is present
        dashboard_url = reverse("dashboard", kwargs={"budget_id": self.budget.id})
        response = self.client.get(dashboard_url)
        
        self.assertEqual(response.status_code, 200)
        delete_url = reverse("expense_item_delete", kwargs={"budget_id": self.budget.id, "pk": expense_item.pk})
        self.assertContains(response, delete_url)
        self.assertContains(response, 'fa-trash-can')

    def test_delete_button_not_present_for_non_deletable_items(self):
        """Test that delete button does not appear for non-deletable items"""
        # Create recurring expense (cannot be deleted)
        expense = Expense.objects.create(
            title="Test Recurring Expense",
            amount=Decimal("100.00"),
            expense_type=Expense.TYPE_ENDLESS_RECURRING,
            start_date=date.today(),
            day_of_month=date.today().day,
            budget=self.budget,
            payee=self.payee
        )
        
        expense_item = ExpenseItem.objects.create(
            expense=expense,
            month=self.current_month,
            due_date=date.today(),
            amount=Decimal("100.00")
        )
        
        # Check dashboard to see if delete button is NOT present
        dashboard_url = reverse("dashboard", kwargs={"budget_id": self.budget.id})
        response = self.client.get(dashboard_url)
        
        self.assertEqual(response.status_code, 200)
        delete_url = reverse("expense_item_delete", kwargs={"budget_id": self.budget.id, "pk": expense_item.pk})
        self.assertNotContains(response, delete_url)

    def test_split_payment_expense_cannot_be_deleted(self):
        """Test that split payment expenses cannot be deleted"""
        # Create split payment expense
        expense = Expense.objects.create(
            title="Test Split Payment Expense",
            amount=Decimal("100.00"),
            expense_type=Expense.TYPE_SPLIT_PAYMENT,
            start_date=date.today(),
            day_of_month=date.today().day,
            budget=self.budget,
            payee=self.payee,
            total_parts=3
        )
        
        expense_item = ExpenseItem.objects.create(
            expense=expense,
            month=self.current_month,
            due_date=date.today(),
            amount=Decimal("100.00")
        )
        
        self.assertFalse(expense_item.can_be_deleted())

    def test_recurring_with_end_expense_cannot_be_deleted(self):
        """Test that recurring with end date expenses cannot be deleted"""
        # Create recurring with end date expense
        expense = Expense.objects.create(
            title="Test Recurring with End Expense",
            amount=Decimal("100.00"),
            expense_type=Expense.TYPE_RECURRING_WITH_END,
            start_date=date.today(),
            day_of_month=date.today().day,
            end_date=date.today() + timedelta(days=30),
            budget=self.budget,
            payee=self.payee
        )
        
        expense_item = ExpenseItem.objects.create(
            expense=expense,
            month=self.current_month,
            due_date=date.today(),
            amount=Decimal("100.00")
        )
        
        self.assertFalse(expense_item.can_be_deleted())