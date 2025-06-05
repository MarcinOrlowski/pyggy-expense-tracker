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


class BudgetBalanceTest(TestCase):
    """Test cases for Budget balance calculation functionality."""
    
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
        self.payee = Payee.objects.create(name='Test Payee')
        
    def test_get_current_balance_no_expenses(self):
        """Test balance calculation when no expenses exist."""
        balance = self.budget.get_current_balance()
        self.assertEqual(balance, Decimal('1000.00'))
    
    def test_get_current_balance_with_pending_expenses(self):
        """Test balance calculation with only pending expenses."""
        # Create expense
        expense = Expense.objects.create(
            title='Test Expense',
            amount=Decimal('200.00'),
            expense_type='one_time',
            start_date=date(2024, 1, 15),
            day_of_month=15,
            budget=self.budget,
            payee=self.payee
        )
        
        # Create pending expense item
        ExpenseItem.objects.create(
            expense=expense,
            month=self.month,
            due_date=date(2024, 1, 15),
            amount=Decimal('200.00'),
            status='pending'
        )
        
        # Balance should be affected by pending expenses (committed funds)
        balance = self.budget.get_current_balance()
        self.assertEqual(balance, Decimal('800.00'))
    
    def test_get_current_balance_with_paid_expenses(self):
        """Test balance calculation with paid expenses."""
        # Create expense
        expense = Expense.objects.create(
            title='Test Expense',
            amount=Decimal('200.00'),
            expense_type='one_time',
            start_date=date(2024, 1, 15),
            day_of_month=15,
            budget=self.budget,
            payee=self.payee
        )
        
        # Create paid expense item
        ExpenseItem.objects.create(
            expense=expense,
            month=self.month,
            due_date=date(2024, 1, 15),
            amount=Decimal('200.00'),
            status='paid'
        )
        
        # Balance should be reduced by paid expenses
        balance = self.budget.get_current_balance()
        self.assertEqual(balance, Decimal('800.00'))
    
    def test_get_current_balance_with_mixed_expenses(self):
        """Test balance calculation with mix of paid and pending expenses."""
        # Create expenses
        expense1 = Expense.objects.create(
            title='Paid Expense',
            amount=Decimal('150.00'),
            expense_type='one_time',
            start_date=date(2024, 1, 10),
            day_of_month=10,
            budget=self.budget,
            payee=self.payee
        )
        
        expense2 = Expense.objects.create(
            title='Pending Expense',
            amount=Decimal('300.00'),
            expense_type='one_time',
            start_date=date(2024, 1, 20),
            day_of_month=20,
            budget=self.budget,
            payee=self.payee
        )
        
        # Create expense items
        ExpenseItem.objects.create(
            expense=expense1,
            month=self.month,
            due_date=date(2024, 1, 10),
            amount=Decimal('150.00'),
            status='paid'
        )
        
        ExpenseItem.objects.create(
            expense=expense2,
            month=self.month,
            due_date=date(2024, 1, 20),
            amount=Decimal('300.00'),
            status='pending'
        )
        
        # Balance should be reduced by all committed expenses (paid + pending)
        balance = self.budget.get_current_balance()
        self.assertEqual(balance, Decimal('550.00'))
    
    def test_get_current_balance_overspent(self):
        """Test balance calculation when overspent (negative balance)."""
        # Create expense that exceeds budget
        expense = Expense.objects.create(
            title='Large Expense',
            amount=Decimal('1200.00'),
            expense_type='one_time',
            start_date=date(2024, 1, 15),
            day_of_month=15,
            budget=self.budget,
            payee=self.payee
        )
        
        # Create paid expense item
        ExpenseItem.objects.create(
            expense=expense,
            month=self.month,
            due_date=date(2024, 1, 15),
            amount=Decimal('1200.00'),
            status='paid'
        )
        
        # Balance should be negative
        balance = self.budget.get_current_balance()
        self.assertEqual(balance, Decimal('-200.00'))
    
    def test_get_current_balance_multiple_paid_expenses(self):
        """Test balance calculation with multiple paid expenses."""
        # Create multiple expenses
        for i, amount in enumerate([Decimal('100.00'), Decimal('250.00'), Decimal('75.50')]):
            expense = Expense.objects.create(
                title=f'Expense {i+1}',
                amount=amount,
                expense_type='one_time',
                start_date=date(2024, 1, 10 + i),
                day_of_month=10 + i,
                budget=self.budget,
                payee=self.payee
            )
            
            ExpenseItem.objects.create(
                expense=expense,
                month=self.month,
                due_date=date(2024, 1, 10 + i),
                amount=amount,
                status='paid'
            )
        
        # Balance should be 1000 - (100 + 250 + 75.50) = 574.50
        balance = self.budget.get_current_balance()
        self.assertEqual(balance, Decimal('574.50'))
    
    def test_get_current_balance_zero_initial_amount(self):
        """Test balance calculation with zero initial amount."""
        zero_budget = Budget.objects.create(
            name='Zero Budget',
            start_date=date(2024, 2, 1),
            initial_amount=Decimal('0.00')
        )
        
        # Balance should be zero with no expenses
        balance = zero_budget.get_current_balance()
        self.assertEqual(balance, Decimal('0.00'))
        
        # Create month and expense for zero budget
        zero_month = Month.objects.create(
            year=2024,
            month=2,
            budget=zero_budget
        )
        
        expense = Expense.objects.create(
            title='Test Expense',
            amount=Decimal('50.00'),
            expense_type='one_time',
            start_date=date(2024, 2, 15),
            day_of_month=15,
            budget=zero_budget,
            payee=self.payee
        )
        
        ExpenseItem.objects.create(
            expense=expense,
            month=zero_month,
            due_date=date(2024, 2, 15),
            amount=Decimal('50.00'),
            status='paid'
        )
        
        # Balance should be negative (overspent from zero)
        balance = zero_budget.get_current_balance()
        self.assertEqual(balance, Decimal('-50.00'))
    
    def test_get_current_balance_only_affects_same_budget(self):
        """Test that balance calculation only includes expenses from the same budget."""
        # Create another budget
        other_budget = Budget.objects.create(
            name='Other Budget',
            start_date=date(2024, 2, 1),
            initial_amount=Decimal('500.00')
        )
        
        other_month = Month.objects.create(
            year=2024,
            month=2,
            budget=other_budget
        )
        
        # Create expense in original budget
        expense1 = Expense.objects.create(
            title='Budget 1 Expense',
            amount=Decimal('100.00'),
            expense_type='one_time',
            start_date=date(2024, 1, 15),
            day_of_month=15,
            budget=self.budget,
            payee=self.payee
        )
        
        ExpenseItem.objects.create(
            expense=expense1,
            month=self.month,
            due_date=date(2024, 1, 15),
            amount=Decimal('100.00'),
            status='paid'
        )
        
        # Create expense in other budget
        expense2 = Expense.objects.create(
            title='Budget 2 Expense',
            amount=Decimal('200.00'),
            expense_type='one_time',
            start_date=date(2024, 2, 15),
            day_of_month=15,
            budget=other_budget,
            payee=self.payee
        )
        
        ExpenseItem.objects.create(
            expense=expense2,
            month=other_month,
            due_date=date(2024, 2, 15),
            amount=Decimal('200.00'),
            status='paid'
        )
        
        # Each budget should only reflect its own expenses
        balance1 = self.budget.get_current_balance()
        balance2 = other_budget.get_current_balance()
        
        self.assertEqual(balance1, Decimal('900.00'))  # 1000 - 100
        self.assertEqual(balance2, Decimal('300.00'))  # 500 - 200


class BudgetListViewTest(TestCase):
    """Test cases for budget list view with balance calculations."""
    
    def setUp(self):
        """Set up test data."""
        self.budget = Budget.objects.create(
            name='Test Budget',
            start_date=date(2024, 1, 1),
            initial_amount=Decimal('1000.00')
        )
    
    def test_budget_list_view_balance_calculation_logic(self):
        """Test that budget list view logic correctly calculates balances."""
        # Test the view logic directly (as fixed in the view)
        budgets = list(Budget.objects.all())
        
        # Simulate what the view does
        for budget in budgets:
            budget.current_balance = budget.get_current_balance()
        
        # Check that balance attribute was added
        for budget in budgets:
            self.assertTrue(hasattr(budget, 'current_balance'))
            self.assertIsInstance(budget.current_balance, Decimal)
            self.assertEqual(budget.current_balance, Decimal('1000.00'))
    
    def test_budget_list_view_with_expenses(self):
        """Test that budget list view calculates balance correctly with expenses."""
        # Create some test data
        month = Month.objects.create(year=2024, month=1, budget=self.budget)
        payee = Payee.objects.create(name='Test Payee')
        
        expense = Expense.objects.create(
            title='Test Expense',
            amount=Decimal('300.00'),
            expense_type='one_time',
            start_date=date(2024, 1, 15),
            day_of_month=15,
            budget=self.budget,
            payee=payee
        )
        
        ExpenseItem.objects.create(
            expense=expense,
            month=month,
            due_date=date(2024, 1, 15),
            amount=Decimal('300.00'),
            status='paid'
        )
        
        # Test the view logic (as fixed in the view)
        budgets = list(Budget.objects.all())
        for budget in budgets:
            budget.current_balance = budget.get_current_balance()
        
        budget = budgets[0]  # Should be our test budget
        
        # Check balance calculation
        expected_balance = Decimal('700.00')  # 1000 - 300
        self.assertEqual(budget.current_balance, expected_balance)
    
    def test_budget_list_template_rendering(self):
        """Test that budget list template can render with balance data."""
        from django.test import RequestFactory
        from django.template import Context, Template
        
        # Add balance to budget (simulating what the view does)
        self.budget.current_balance = self.budget.get_current_balance()
        
        # Test template rendering with new amount_with_class filter
        template_content = '''
        {% load currency_tags %}
        <td class="text-right">
            {{ budget.current_balance|amount_with_class }}
        </td>
        '''
        
        template = Template(template_content)
        context = Context({'budget': self.budget})
        rendered = template.render(context)
        
        # Should contain the formatted currency with appropriate class
        self.assertIn('$1,000.00', rendered)
        self.assertIn('text-right', rendered)
        self.assertIn('amount-positive', rendered)
        # Should not have negative styling for positive balance
        self.assertNotIn('amount-negative', rendered)
    
    def test_budget_list_template_negative_balance_styling(self):
        """Test that negative balances get proper CSS styling."""
        from django.template import Context, Template
        
        # Set negative balance
        self.budget.current_balance = Decimal('-100.00')
        
        template_content = '''
        {% load currency_tags %}
        <td class="text-right">
            {{ budget.current_balance|amount_with_class }}
        </td>
        '''
        
        template = Template(template_content)
        context = Context({'budget': self.budget})
        rendered = template.render(context)
        
        # Should contain the formatted currency with negative styling
        self.assertIn('-$100.00', rendered)
        self.assertIn('amount-negative', rendered)
        # Should not have positive styling for negative balance
        self.assertNotIn('amount-positive', rendered)