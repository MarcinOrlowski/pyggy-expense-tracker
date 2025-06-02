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
    
    def test_budget_name_duplicates_allowed(self):
        """Test that budget names can be duplicated."""
        # Should not raise an error
        budget2 = Budget.objects.create(
            name='Test Budget',  # Same name as setUp budget
            start_date=date(2024, 2, 1),
            initial_amount=Decimal('500.00')
        )
        self.assertEqual(budget2.name, 'Test Budget')
        self.assertEqual(Budget.objects.filter(name='Test Budget').count(), 2)
    
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
    
    def test_budget_deletion_cascades(self):
        """Test that budget deletion cascades to months."""
        month_id = self.month.id
        self.budget.delete()
        # Budget and month should both be deleted
        self.assertEqual(Budget.objects.filter(id=self.budget.id).count(), 0)
        self.assertEqual(Month.objects.filter(id=month_id).count(), 0)
    
    def test_month_budget_access(self):
        """Test that month can access its budget."""
        self.assertEqual(self.month.budget, self.budget)
        self.assertEqual(self.month.budget.name, 'Test Budget')


class BudgetRelationshipTest(TestCase):
    """Test cases for budget relationships with other models."""
    
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
    
    def test_budget_has_months(self):
        """Test that budget can access its months."""
        months = self.budget.month_set.all()
        self.assertEqual(months.count(), 2)
        self.assertIn(self.month1, months)
        self.assertIn(self.month2, months)
    
    def test_budget_can_delete_method(self):
        """Test the can_be_deleted method."""
        # Budget with months cannot be deleted
        self.assertFalse(self.budget.can_be_deleted())
        
        # Budget without months can be deleted
        empty_budget = Budget.objects.create(
            name='Empty Budget',
            start_date=date(2024, 3, 1)
        )
        self.assertTrue(empty_budget.can_be_deleted())
    
    def test_multiple_budgets_separation(self):
        """Test that data is properly separated between budgets."""
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
        
        # Check that months are properly separated
        self.assertEqual(self.budget.month_set.count(), 2)
        self.assertEqual(budget2.month_set.count(), 1)
        self.assertEqual(budget2.month_set.first(), month3)


class ProcessNewMonthWithBudgetTest(TestCase):
    """Test cases for process_new_month with budget functionality."""
    
    def setUp(self):
        """Clear any existing default budget from migrations."""
        Budget.objects.filter(name='Default').delete()
    
    def test_process_new_month_requires_budget_parameter(self):
        """Test that process_new_month requires budget parameter."""
        # This test documents that the function now requires a budget parameter
        # If called without a budget, it should raise TypeError
        with self.assertRaises(TypeError) as context:
            process_new_month(2024, 1)  # Missing budget parameter
        
        self.assertIn("missing 1 required positional argument: 'budget'", str(context.exception))
    
    def test_process_new_month_with_budget(self):
        """Test that process_new_month works with provided budget."""
        # Ensure no budgets exist
        self.assertEqual(Budget.objects.count(), 0)
        
        # Create Default budget
        default_budget = Budget.objects.create(
            name='Default',
            start_date=date(2024, 1, 1),
            initial_amount=Decimal('0')
        )
        
        # Now it should work
        month = process_new_month(2024, 1, default_budget)
        self.assertEqual(month.budget, default_budget)
    
    def test_process_new_month_uses_existing_default_budget(self):
        """Test that process_new_month uses provided budget."""
        # Create default budget
        existing_budget = Budget.objects.create(
            name='Default',
            start_date=date(2023, 1, 1),
            initial_amount=Decimal('1000.00')
        )
        
        # Process a new month
        month = process_new_month(2024, 1, existing_budget)
        
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
        processed_month = process_new_month(2024, 1, budget)
        
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