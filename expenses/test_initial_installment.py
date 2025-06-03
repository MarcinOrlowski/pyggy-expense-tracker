from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date
from expenses.models import Budget, Expense, ExpenseItem, Month
from expenses.services import create_expense_items_for_month, check_expense_completion
from expenses.forms import ExpenseForm


class InitialInstallmentModelTest(TestCase):
    """Test cases for initial_installment field in Expense model."""
    
    def setUp(self):
        """Set up test data."""
        self.budget = Budget.objects.create(
            name="Test Budget",
            start_date=date.today()
        )
        
    def test_split_payment_with_initial_installment_validation_success(self):
        """Test valid split payment with initial_installment."""
        expense = Expense(
            budget=self.budget,
            title="Test Split Payment",
            expense_type=Expense.TYPE_SPLIT_PAYMENT,
            total_amount=Decimal('100.00'),
            installments_count=10,
            initial_installment=5,
            started_at=date.today()
        )
        # Should not raise validation error
        expense.full_clean()
        
    def test_split_payment_initial_installment_zero_valid(self):
        """Test split payment with initial_installment=0 (default behavior)."""
        expense = Expense(
            budget=self.budget,
            title="Test Split Payment",
            expense_type=Expense.TYPE_SPLIT_PAYMENT,
            total_amount=Decimal('100.00'),
            installments_count=10,
            initial_installment=0,
            started_at=date.today()
        )
        expense.full_clean()
        
    def test_split_payment_initial_installment_max_valid(self):
        """Test split payment with initial_installment at maximum (installments_count - 1)."""
        expense = Expense(
            budget=self.budget,
            title="Test Split Payment",
            expense_type=Expense.TYPE_SPLIT_PAYMENT,
            total_amount=Decimal('100.00'),
            installments_count=10,
            initial_installment=9,
            started_at=date.today()
        )
        expense.full_clean()
        
    def test_split_payment_initial_installment_negative_invalid(self):
        """Test split payment with negative initial_installment fails validation."""
        expense = Expense(
            budget=self.budget,
            title="Test Split Payment",
            expense_type=Expense.TYPE_SPLIT_PAYMENT,
            total_amount=Decimal('100.00'),
            installments_count=10,
            initial_installment=-1,
            started_at=date.today()
        )
        with self.assertRaises(ValidationError) as cm:
            expense.full_clean()
        self.assertIn('Initial installment cannot be negative', str(cm.exception))
        
    def test_split_payment_initial_installment_too_high_invalid(self):
        """Test split payment with initial_installment >= installments_count fails validation."""
        expense = Expense(
            budget=self.budget,
            title="Test Split Payment",
            expense_type=Expense.TYPE_SPLIT_PAYMENT,
            total_amount=Decimal('100.00'),
            installments_count=10,
            initial_installment=10,
            started_at=date.today()
        )
        with self.assertRaises(ValidationError) as cm:
            expense.full_clean()
        self.assertIn('Initial installment must be less than total installments count', str(cm.exception))
        
    def test_non_split_payment_with_initial_installment_invalid(self):
        """Test non-split payment with initial_installment > 0 fails validation."""
        expense = Expense(
            budget=self.budget,
            title="Test Recurring",
            expense_type=Expense.TYPE_ENDLESS_RECURRING,
            total_amount=Decimal('100.00'),
            installments_count=0,
            initial_installment=5,
            started_at=date.today()
        )
        with self.assertRaises(ValidationError) as cm:
            expense.full_clean()
        self.assertIn('Initial installment can only be used with split payment expenses', str(cm.exception))
        
    def test_non_split_payment_with_zero_initial_installment_valid(self):
        """Test non-split payment with initial_installment=0 is valid."""
        expense = Expense(
            budget=self.budget,
            title="Test Recurring",
            expense_type=Expense.TYPE_ENDLESS_RECURRING,
            total_amount=Decimal('100.00'),
            installments_count=0,
            initial_installment=0,
            started_at=date.today()
        )
        expense.full_clean()


class InitialInstallmentServiceTest(TestCase):
    """Test cases for initial_installment in service functions."""
    
    def setUp(self):
        """Set up test data."""
        self.budget = Budget.objects.create(
            name="Test Budget",
            start_date=date.today()
        )
        self.month = Month.objects.create(
            budget=self.budget,
            year=date.today().year,
            month=date.today().month
        )
        
    def test_create_expense_items_respects_initial_installment(self):
        """Test that create_expense_items_for_month respects initial_installment."""
        # Create split payment starting from installment 3 (0-based)
        expense = Expense.objects.create(
            budget=self.budget,
            title="Partial Split Payment",
            expense_type=Expense.TYPE_SPLIT_PAYMENT,
            total_amount=Decimal('100.00'),
            installments_count=10,
            initial_installment=3,
            started_at=date.today()
        )
        
        # Should create items for remaining 7 installments (10 - 3)
        items = create_expense_items_for_month(expense, self.month)
        self.assertEqual(len(items), 1)  # One item per month call
        
        # Continue creating items until we reach the limit
        for i in range(6):  # 6 more items to reach 7 total
            month_obj = Month.objects.create(
                budget=self.budget,
                year=2026,  # Use different year to avoid conflicts
                month=i + 1
            )
            items = create_expense_items_for_month(expense, month_obj)
            
        # Total items created should be 7 (installments_count - initial_installment)
        total_items = ExpenseItem.objects.filter(expense=expense).count()
        self.assertEqual(total_items, 7)
        
        # Try to create one more - should not create anything
        extra_month = Month.objects.create(
            budget=self.budget,
            year=2027,
            month=1
        )
        items = create_expense_items_for_month(expense, extra_month)
        self.assertEqual(len(items), 0)
        
    def test_check_expense_completion_with_initial_installment(self):
        """Test expense completion logic with initial_installment."""
        expense = Expense.objects.create(
            budget=self.budget,
            title="Partial Split Payment",
            expense_type=Expense.TYPE_SPLIT_PAYMENT,
            total_amount=Decimal('100.00'),
            installments_count=10,
            initial_installment=7,  # Only 3 installments to pay
            started_at=date.today()
        )
        
        # Create 3 expense items
        for i in range(3):
            ExpenseItem.objects.create(
                expense=expense,
                month=self.month,
                amount=Decimal('100.00'),
                due_date=date.today(),
                status='pending'
            )
        
        # Should not be complete yet
        self.assertFalse(check_expense_completion(expense))
        self.assertIsNone(expense.closed_at)
        
        # Pay 2 items - still not complete
        items = ExpenseItem.objects.filter(expense=expense)[:2]
        for item in items:
            item.status = 'paid'
            item.save()
            
        self.assertFalse(check_expense_completion(expense))
        
        # Pay the last item - should be complete
        remaining_item = ExpenseItem.objects.filter(expense=expense, status='pending').first()
        remaining_item.status = 'paid'
        remaining_item.save()
        
        self.assertTrue(check_expense_completion(expense))
        expense.refresh_from_db()
        self.assertIsNotNone(expense.closed_at)


class InitialInstallmentFormTest(TestCase):
    """Test cases for initial_installment in ExpenseForm."""
    
    def setUp(self):
        """Set up test data."""
        self.budget = Budget.objects.create(
            name="Test Budget",
            start_date=date.today()
        )
        
    def test_form_includes_initial_installment_field(self):
        """Test that form includes initial_installment field."""
        form = ExpenseForm(budget=self.budget)
        self.assertIn('initial_installment', form.fields)
        
    def test_form_validation_split_payment_valid_initial_installment(self):
        """Test form validation for valid split payment with initial_installment."""
        form_data = {
            'title': 'Test Split Payment',
            'expense_type': Expense.TYPE_SPLIT_PAYMENT,
            'total_amount': '100.00',
            'installments_count': 10,
            'initial_installment': 5,
            'started_at': date.today().strftime('%Y-%m-%d'),
        }
        form = ExpenseForm(data=form_data, budget=self.budget)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
    def test_form_validation_split_payment_invalid_initial_installment(self):
        """Test form validation for invalid initial_installment."""
        form_data = {
            'title': 'Test Split Payment',
            'expense_type': Expense.TYPE_SPLIT_PAYMENT,
            'total_amount': '100.00',
            'installments_count': 10,
            'initial_installment': 15,  # Invalid: >= installments_count
            'started_at': date.today().strftime('%Y-%m-%d'),
        }
        form = ExpenseForm(data=form_data, budget=self.budget)
        self.assertFalse(form.is_valid())
        self.assertIn('Initial installment must be less than total installments count', 
                     str(form.errors))
        
    def test_form_validation_non_split_payment_with_initial_installment(self):
        """Test form validation for non-split payment with initial_installment."""
        form_data = {
            'title': 'Test Recurring',
            'expense_type': Expense.TYPE_ENDLESS_RECURRING,
            'total_amount': '100.00',
            'installments_count': 0,
            'initial_installment': 5,  # Invalid for non-split payment
            'started_at': date.today().strftime('%Y-%m-%d'),
        }
        form = ExpenseForm(data=form_data, budget=self.budget)
        self.assertFalse(form.is_valid())
        self.assertIn('Initial installment can only be used with split payment expenses',
                     str(form.errors))
        
    def test_form_initial_installment_read_only_on_edit(self):
        """Test that initial_installment field is read-only when editing existing expense."""
        expense = Expense.objects.create(
            budget=self.budget,
            title="Test Split Payment",
            expense_type=Expense.TYPE_SPLIT_PAYMENT,
            total_amount=Decimal('100.00'),
            installments_count=10,
            initial_installment=5,
            started_at=date.today()
        )
        
        form = ExpenseForm(instance=expense, budget=self.budget)
        self.assertTrue(form.fields['initial_installment'].disabled)
        self.assertIn('cannot be changed after expense creation', 
                     form.fields['initial_installment'].help_text)
        
    def test_form_initial_installment_editable_on_create(self):
        """Test that initial_installment field is editable when creating new expense."""
        form = ExpenseForm(budget=self.budget)
        self.assertFalse(form.fields['initial_installment'].disabled)


class InitialInstallmentIntegrationTest(TestCase):
    """Integration tests for initial_installment feature."""
    
    def setUp(self):
        """Set up test data."""
        self.budget = Budget.objects.create(
            name="Test Budget",
            start_date=date.today()
        )
        
    def test_complete_workflow_partial_split_payment(self):
        """Test complete workflow for partial split payment."""
        # Create split payment starting from installment 8 out of 10
        expense = Expense.objects.create(
            budget=self.budget,
            title="Car Loan (Started Mid-Term)",
            expense_type=Expense.TYPE_SPLIT_PAYMENT,
            total_amount=Decimal('500.00'),
            installments_count=10,
            initial_installment=8,  # Only 2 payments remaining
            started_at=date.today()
        )
        
        # Create first month and generate expense items
        month1 = Month.objects.create(
            budget=self.budget,
            year=date.today().year,
            month=date.today().month
        )
        items1 = create_expense_items_for_month(expense, month1)
        self.assertEqual(len(items1), 1)
        
        # Create second month and generate expense items
        next_month = date.today().month + 1 if date.today().month < 12 else 1
        next_year = date.today().year if date.today().month < 12 else date.today().year + 1
        
        month2 = Month.objects.create(
            budget=self.budget,
            year=next_year,
            month=next_month
        )
        items2 = create_expense_items_for_month(expense, month2)
        self.assertEqual(len(items2), 1)
        
        # Try third month - should not create any items (only 2 remaining)
        third_month = next_month + 1 if next_month < 12 else 1
        third_year = next_year if next_month < 12 else next_year + 1
        
        month3 = Month.objects.create(
            budget=self.budget,
            year=third_year,
            month=third_month
        )
        items3 = create_expense_items_for_month(expense, month3)
        self.assertEqual(len(items3), 0)
        
        # Total items should be 2
        total_items = ExpenseItem.objects.filter(expense=expense).count()
        self.assertEqual(total_items, 2)
        
        # Pay first installment - expense should not be complete
        items1[0].status = 'paid'
        items1[0].save()
        self.assertFalse(check_expense_completion(expense))
        
        # Pay second installment - expense should be complete
        items2[0].status = 'paid'
        items2[0].save()
        self.assertTrue(check_expense_completion(expense))
        
        expense.refresh_from_db()
        self.assertIsNotNone(expense.closed_at)