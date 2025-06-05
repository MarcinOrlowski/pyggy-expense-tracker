from django.test import TestCase
from datetime import date
from decimal import Decimal
from expenses.models import Budget, Month, Expense, ExpenseItem, Payee
from expenses.services import create_expense_items_for_month, handle_new_expense


class DueDateMonthProcessingTestCase(TestCase):
    """Test cases for month processing using expense due_date field."""
    
    def setUp(self):
        """Set up test data."""
        self.budget = Budget.objects.create(
            name="Test Budget",
            start_date=date.today(),
            initial_amount=Decimal('1000.00')
        )
        
        self.payee = Payee.objects.create(name="Test Payee")
    
    def test_one_time_expense_created_in_due_date_month(self):
        """Test that one-time expenses are created in the month matching their due_date."""
        # Create a month for February 2024
        february_month = Month.objects.create(
            budget=self.budget,
            year=2024,
            month=2
        )
        
        # Create a one-time expense with day_of_month=20
        expense = Expense.objects.create(
            budget=self.budget,
            payee=self.payee,
            title="Test One-Time Expense",
            expense_type=Expense.TYPE_ONE_TIME,
            amount=Decimal('100.00'),
            start_date=date(2024, 2, 20),  # Started in February 
            day_of_month=20
        )
        
        # Process February month - should create expense item
        items = create_expense_items_for_month(expense, february_month)
        
        # Should create one item
        self.assertEqual(len(items), 1)
        
        # Item should be in February month with correct due date
        item = items[0]
        self.assertEqual(item.month, february_month)
        self.assertEqual(item.due_date, date(2024, 2, 20))
        self.assertEqual(item.amount, Decimal('100.00'))
    
    def test_one_time_expense_created_regardless_of_start_date(self):
        """Test that one-time expenses are created when processed, even if due_date < start_date."""
        # Create a month for January 2024
        january_month = Month.objects.create(
            budget=self.budget,
            year=2024,
            month=1
        )
        
        # Create a one-time expense that starts in February but is processed in January
        expense = Expense.objects.create(
            budget=self.budget,
            payee=self.payee,
            title="Test One-Time Expense",
            expense_type=Expense.TYPE_ONE_TIME,
            amount=Decimal('100.00'),
            start_date=date(2024, 2, 15),  # Started in February
            day_of_month=15,
        )
        
        # Process January month - should create expense item
        # due_date (Jan 15) will be calculated for the processed month
        items = create_expense_items_for_month(expense, january_month)
        
        # Should create one item
        self.assertEqual(len(items), 1)
        
        # Item should have correct due_date for January
        item = items[0]
        self.assertEqual(item.due_date, date(2024, 1, 15))
    
    def test_handle_new_expense_uses_due_date_for_one_time(self):
        """Test that handle_new_expense uses due_date for one-time expenses."""
        # Create current month (February 2024)
        february_month = Month.objects.create(
            budget=self.budget,
            year=2024,
            month=2
        )
        
        # Create a one-time expense that starts in January but is due in February
        expense = Expense.objects.create(
            budget=self.budget,
            payee=self.payee,
            title="Test One-Time Expense",
            expense_type=Expense.TYPE_ONE_TIME,
            amount=Decimal('100.00'),
            start_date=date(2024, 1, 15),  # Started in January (not current month)
            day_of_month=15,
        )
        
        # Handle the new expense - should create item because due date is in current month
        handle_new_expense(expense, self.budget)
        
        # Should have created an expense item
        items = ExpenseItem.objects.filter(expense=expense)
        self.assertEqual(items.count(), 1)
        
        # Item should be in February with correct due date
        item = items.first()
        self.assertIsNotNone(item)
        if item is not None:
            self.assertEqual(item.month, february_month)
            self.assertEqual(item.due_date, date(2024, 2, 15))
    
    def test_recurring_expenses_still_use_started_at(self):
        """Test that recurring expenses still use started_at for month processing."""
        # Create a month for January 2024
        january_month = Month.objects.create(
            budget=self.budget,
            year=2024,
            month=1
        )
        
        # Create an endless recurring expense
        expense = Expense.objects.create(
            budget=self.budget,
            payee=self.payee,
            title="Test Recurring Expense",
            expense_type=Expense.TYPE_ENDLESS_RECURRING,
            amount=Decimal('50.00'),
            start_date=date(2024, 1, 15),  # Started in January
            day_of_month=15,
        )
        
        # Process January month - should create expense item based on started_at
        items = create_expense_items_for_month(expense, january_month)
        
        # Should create one item
        self.assertEqual(len(items), 1)
        
        # Item should be in January month with due date calculated from started_at day
        item = items[0]
        self.assertEqual(item.month, january_month)
        self.assertEqual(item.due_date, date(2024, 1, 15))  # Uses started_at day in target month
        self.assertEqual(item.amount, Decimal('50.00'))
    
    def test_one_time_expense_with_start_date_after_due_date(self):
        """Test one-time expense where start_date is after due_date (your scenario)."""
        # Create a month for May 2025
        may_month = Month.objects.create(
            budget=self.budget,
            year=2025,
            month=5
        )
        
        # Create a one-time expense with start date after due date
        expense = Expense.objects.create(
            budget=self.budget,
            payee=self.payee,
            title="Test One-Time Expense",
            expense_type=Expense.TYPE_ONE_TIME,
            amount=Decimal('100.00'),
            start_date=date(2025, 6, 1),   # Started in June
            day_of_month=1,
        )
        
        # Process May month - should create expense item based on due_date
        items = create_expense_items_for_month(expense, may_month)
        
        # Should create one item
        self.assertEqual(len(items), 1)
        
        # Item should be in May month with correct due date
        item = items[0]
        self.assertEqual(item.month, may_month)
        self.assertEqual(item.due_date, date(2025, 5, 1))
        self.assertEqual(item.amount, Decimal('100.00'))
    
    def test_one_time_expense_future_start_date_creates_item_in_processed_month(self):
        """Test that one-time expenses with future start_date can be created in earlier months."""
        # Create a month for May 2025
        may_month = Month.objects.create(
            budget=self.budget,
            year=2025,
            month=5
        )
        
        # Create a one-time expense with start_date in June (future)
        expense = Expense.objects.create(
            budget=self.budget,
            payee=self.payee,
            title="Future Start Date Expense",
            expense_type=Expense.TYPE_ONE_TIME,
            amount=Decimal('150.00'),
            start_date=date(2025, 6, 10),   # Starts in June
            day_of_month=10,
        )
        
        # Process May month - should create expense item
        items = create_expense_items_for_month(expense, may_month)
        
        # Should create one item
        self.assertEqual(len(items), 1)
        
        # Item should be in May month with correct due date
        item = items[0]
        self.assertEqual(item.month, may_month)
        self.assertEqual(item.due_date, date(2025, 5, 10))
        self.assertEqual(item.amount, Decimal('150.00'))
        
        # Verify no items exist before this test
        self.assertEqual(ExpenseItem.objects.filter(expense=expense).count(), 1)