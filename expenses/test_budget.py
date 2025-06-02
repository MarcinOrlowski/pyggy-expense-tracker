from django.test import TestCase, TransactionTestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from decimal import Decimal
from datetime import date
from expenses.models import Budget, Month, Expense, ExpenseItem, Payee, PaymentMethod
from expenses.services import process_new_month


class BudgetModelTest(TestCase):
    """Test cases for the Budget model."""
    
    def setUp(self):
        """Set up test data."""
        self.budget = Budget.objects.create(
            name='Test Budget',
            start_date=date(2024, 1, 1),
            initial_amount=Decimal('1000.00')
        )
    
    def test_budget_creation(self):
        """Test budget can be created with valid data."""
        self.assertEqual(self.budget.name, 'Test Budget')
        self.assertEqual(self.budget.start_date, date(2024, 1, 1))
        self.assertEqual(self.budget.initial_amount, Decimal('1000.00'))
        self.assertIsNotNone(self.budget.created_at)
        self.assertIsNotNone(self.budget.updated_at)
    
    def test_budget_str_representation(self):
        """Test string representation of budget."""
        self.assertEqual(str(self.budget), 'Test Budget')
    
    def test_budget_name_uniqueness(self):
        """Test that budget names must be unique."""
        with self.assertRaises(IntegrityError):
            Budget.objects.create(
                name='Test Budget',  # Same name as setUp budget
                start_date=date(2024, 2, 1),
                initial_amount=Decimal('500.00')
            )
    
    def test_budget_default_initial_amount(self):
        """Test that initial_amount defaults to 0."""
        budget = Budget.objects.create(
            name='Zero Budget',
            start_date=date(2024, 1, 1)
        )
        self.assertEqual(budget.initial_amount, Decimal('0'))
    
    def test_budget_negative_initial_amount_validation(self):
        """Test that negative initial amounts are not allowed."""
        budget = Budget(
            name='Invalid Budget',
            start_date=date(2024, 1, 1),
            initial_amount=Decimal('-100.00')
        )
        with self.assertRaises(ValidationError):
            budget.full_clean()


class BudgetMonthRelationshipTest(TestCase):
    """Test cases for Budget-Month relationship."""
    
    def setUp(self):
        """Set up test data."""
        self.budget = Budget.objects.create(
            name='Test Budget',
            start_date=date(2024, 1, 1),
            initial_amount=Decimal('1000.00')
        )
        self.month = Month.objects.create(
            year=2024,
            month=1,
            budget=self.budget
        )
    
    def test_month_requires_budget(self):
        """Test that month must have a budget."""
        with self.assertRaises(IntegrityError):
            Month.objects.create(
                year=2024,
                month=2,
                budget=None
            )
    
    def test_budget_month_relationship(self):
        """Test that budget can access its months."""
        self.assertEqual(self.budget.month_set.count(), 1)
        self.assertEqual(self.budget.month_set.first(), self.month)
    
    def test_budget_deletion_protection(self):
        """Test that budget cannot be deleted if it has months."""
        with self.assertRaises(ProtectedError):
            self.budget.delete()
    
    def test_month_budget_access(self):
        """Test that month can access its budget."""
        self.assertEqual(self.month.budget, self.budget)
        self.assertEqual(self.month.budget.name, 'Test Budget')


class BudgetCalculationTest(TestCase):
    """Test cases for budget calculation methods."""
    
    def setUp(self):
        """Set up test data."""
        self.budget = Budget.objects.create(
            name='Test Budget',
            start_date=date(2024, 1, 1),
            initial_amount=Decimal('1000.00')
        )
        self.month1 = Month.objects.create(
            year=2024,
            month=1,
            budget=self.budget
        )
        self.month2 = Month.objects.create(
            year=2024,
            month=2,
            budget=self.budget
        )
        
        # Create a payee and payment method for expenses
        self.payee = Payee.objects.create(name='Test Payee')
        self.payment_method = PaymentMethod.objects.create(name='Cash')
        
        # Create expenses
        self.expense1 = Expense.objects.create(
            payee=self.payee,
            title='Expense 1',
            expense_type=Expense.TYPE_ONE_TIME,
            total_amount=Decimal('100.00'),
            started_at=date(2024, 1, 1)
        )
        self.expense2 = Expense.objects.create(
            payee=self.payee,
            title='Expense 2',
            expense_type=Expense.TYPE_ONE_TIME,
            total_amount=Decimal('200.00'),
            started_at=date(2024, 2, 1)
        )
    
    def test_get_total_expenses_empty(self):
        """Test total expenses calculation with no expense items."""
        total = self.budget.get_total_expenses()
        self.assertEqual(total, Decimal('0.00'))
    
    def test_get_total_expenses_with_items(self):
        """Test total expenses calculation with expense items."""
        # Create expense items
        ExpenseItem.objects.create(
            expense=self.expense1,
            month=self.month1,
            due_date=date(2024, 1, 15),
            amount=Decimal('100.00'),
            status='pending'
        )
        ExpenseItem.objects.create(
            expense=self.expense2,
            month=self.month2,
            due_date=date(2024, 2, 15),
            amount=Decimal('200.00'),
            status='pending'
        )
        
        total = self.budget.get_total_expenses()
        self.assertEqual(total, Decimal('300.00'))
    
    def test_get_balance_positive(self):
        """Test balance calculation with positive result."""
        # Create expense items
        ExpenseItem.objects.create(
            expense=self.expense1,
            month=self.month1,
            due_date=date(2024, 1, 15),
            amount=Decimal('100.00'),
            status='pending'
        )
        
        balance = self.budget.get_balance()
        self.assertEqual(balance, Decimal('900.00'))  # 1000 - 100
    
    def test_get_balance_negative(self):
        """Test balance calculation with negative result."""
        # Create expense items that exceed initial amount
        ExpenseItem.objects.create(
            expense=self.expense1,
            month=self.month1,
            due_date=date(2024, 1, 15),
            amount=Decimal('600.00'),
            status='pending'
        )
        ExpenseItem.objects.create(
            expense=self.expense2,
            month=self.month2,
            due_date=date(2024, 2, 15),
            amount=Decimal('500.00'),
            status='pending'
        )
        
        balance = self.budget.get_balance()
        self.assertEqual(balance, Decimal('-100.00'))  # 1000 - 1100
    
    def test_get_total_expenses_multiple_budgets(self):
        """Test that expenses are correctly separated by budget."""
        # Create another budget
        budget2 = Budget.objects.create(
            name='Budget 2',
            start_date=date(2024, 1, 1),
            initial_amount=Decimal('500.00')
        )
        month3 = Month.objects.create(
            year=2024,
            month=3,
            budget=budget2
        )
        
        # Create expense items for different budgets
        ExpenseItem.objects.create(
            expense=self.expense1,
            month=self.month1,  # budget1
            due_date=date(2024, 1, 15),
            amount=Decimal('100.00'),
            status='pending'
        )
        ExpenseItem.objects.create(
            expense=self.expense2,
            month=month3,  # budget2
            due_date=date(2024, 3, 15),
            amount=Decimal('200.00'),
            status='pending'
        )
        
        # Check totals are separate
        self.assertEqual(self.budget.get_total_expenses(), Decimal('100.00'))
        self.assertEqual(budget2.get_total_expenses(), Decimal('200.00'))


class ProcessNewMonthWithBudgetTest(TestCase):
    """Test cases for process_new_month with budget functionality."""
    
    def setUp(self):
        """Clear any existing default budget from migrations."""
        Budget.objects.filter(name='Default').delete()
    
    def test_process_new_month_creates_default_budget(self):
        """Test that process_new_month creates default budget if none exists."""
        # Ensure no budgets exist
        self.assertEqual(Budget.objects.count(), 0)
        
        # Process a new month
        month = process_new_month(2024, 1)
        
        # Check that default budget was created
        self.assertEqual(Budget.objects.count(), 1)
        default_budget = Budget.objects.first()
        self.assertEqual(default_budget.name, 'Default')
        self.assertEqual(default_budget.initial_amount, Decimal('0'))
        
        # Check that month is linked to the budget
        self.assertEqual(month.budget, default_budget)
    
    def test_process_new_month_uses_existing_default_budget(self):
        """Test that process_new_month uses existing default budget."""
        # Create default budget
        existing_budget = Budget.objects.create(
            name='Default',
            start_date=date(2023, 1, 1),
            initial_amount=Decimal('1000.00')
        )
        
        # Process a new month
        month = process_new_month(2024, 1)
        
        # Check that no new budget was created
        self.assertEqual(Budget.objects.count(), 1)
        
        # Check that month uses existing budget
        self.assertEqual(month.budget, existing_budget)
        self.assertEqual(month.budget.initial_amount, Decimal('1000.00'))
    
    def test_process_new_month_assigns_budget_to_existing_month(self):
        """Test that existing months get budget assigned properly."""
        # Get or create default budget
        budget, _ = Budget.objects.get_or_create(
            name='Default',
            defaults={
                'start_date': date(2024, 1, 1),
                'initial_amount': Decimal('0')
            }
        )
        
        # Create a month with budget
        month = Month.objects.create(
            year=2024,
            month=1,
            budget=budget
        )
        
        # Process the same month again
        processed_month = process_new_month(2024, 1)
        
        # Should return existing month with budget
        self.assertEqual(processed_month, month)
        self.assertEqual(processed_month.budget, budget)


class BudgetOrderingTest(TestCase):
    """Test cases for budget ordering."""
    
    def setUp(self):
        """Clear any existing budgets from migrations."""
        Budget.objects.all().delete()
    
    def test_budget_ordering_by_name(self):
        """Test that budgets are ordered by name."""
        Budget.objects.create(
            name='Zebra Budget',
            start_date=date(2024, 1, 1)
        )
        Budget.objects.create(
            name='Alpha Budget',
            start_date=date(2024, 1, 1)
        )
        Budget.objects.create(
            name='Middle Budget',
            start_date=date(2024, 1, 1)
        )
        
        budgets = list(Budget.objects.all().values_list('name', flat=True))
        self.assertEqual(budgets, ['Alpha Budget', 'Middle Budget', 'Zebra Budget'])