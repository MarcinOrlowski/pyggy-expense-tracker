from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.template import Context, Template
from datetime import date, datetime
from unittest.mock import patch
from expenses.models import Budget, Month, Expense, ExpenseItem, Payee, Settings
from expenses.services import SettingsService


class CalendarHighlightingTest(TestCase):
    """Test cases for calendar weekday highlighting logic."""
    
    def setUp(self):
        """Set up test data."""
        # Clear any existing settings
        Settings.objects.all().delete()
        # Create test settings
        self.settings = Settings.objects.create(
            locale='en_US',
            currency='USD'
        )
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test budget
        self.budget = Budget.objects.create(
            name='Test Budget',
            start_date=date(2024, 1, 1),
            initial_amount=1000.00
        )
        
        # Create test month
        self.month = Month.objects.create(
            month=1,
            year=2024,
            budget=self.budget
        )
        
        self.client = Client()
    
    def test_weekday_highlighting_current_month(self):
        """Test that weekday headers are highlighted when viewing current month."""
        # Mock today to be January 15, 2024 (Monday = weekday 0)
        mock_today = date(2024, 1, 15)
        
        template = Template('''
            {% load currency_tags %}
            <div class="calendar-weekday {% if current_weekday == 0 and display_month == today.month and display_year == today.year %}calendar-weekday--today{% endif %}">Mon</div>
            <div class="calendar-weekday {% if current_weekday == 1 and display_month == today.month and display_year == today.year %}calendar-weekday--today{% endif %}">Tue</div>
            <div class="calendar-weekday {% if current_weekday == 2 and display_month == today.month and display_year == today.year %}calendar-weekday--today{% endif %}">Wed</div>
            <div class="calendar-weekday {% if current_weekday == 3 and display_month == today.month and display_year == today.year %}calendar-weekday--today{% endif %}">Thu</div>
            <div class="calendar-weekday {% if current_weekday == 4 and display_month == today.month and display_year == today.year %}calendar-weekday--today{% endif %}">Fri</div>
            <div class="calendar-weekday calendar-weekday--weekend {% if current_weekday == 5 and display_month == today.month and display_year == today.year %}calendar-weekday--today{% endif %}">Sat</div>
            <div class="calendar-weekday calendar-weekday--weekend {% if current_weekday == 6 and display_month == today.month and display_year == today.year %}calendar-weekday--today{% endif %}">Sun</div>
        ''')
        
        # Test viewing current month (January 2024) on Monday
        context = Context({
            'current_weekday': 0,  # Monday
            'display_month': 1,    # January
            'display_year': 2024,
            'today': mock_today
        })
        
        result = template.render(context)
        
        # Monday should be highlighted (contains calendar-weekday--today)
        self.assertIn('calendar-weekday--today', result)
        # Count occurrences - should be exactly 1 (only Monday)
        self.assertEqual(result.count('calendar-weekday--today'), 1)
        
        # Verify Monday specifically is highlighted
        lines = result.strip().split('\n')
        monday_line = [line for line in lines if 'Mon</div>' in line][0]
        self.assertIn('calendar-weekday--today', monday_line)
    
    def test_weekday_highlighting_different_month(self):
        """Test that weekday headers are NOT highlighted when viewing different month."""
        mock_today = date(2024, 1, 15)  # Monday in January
        
        template = Template('''
            {% load currency_tags %}
            <div class="calendar-weekday {% if current_weekday == 0 and display_month == today.month and display_year == today.year %}calendar-weekday--today{% endif %}">Mon</div>
            <div class="calendar-weekday {% if current_weekday == 1 and display_month == today.month and display_year == today.year %}calendar-weekday--today{% endif %}">Tue</div>
            <div class="calendar-weekday {% if current_weekday == 2 and display_month == today.month and display_year == today.year %}calendar-weekday--today{% endif %}">Wed</div>
            <div class="calendar-weekday {% if current_weekday == 3 and display_month == today.month and display_year == today.year %}calendar-weekday--today{% endif %}">Thu</div>
            <div class="calendar-weekday {% if current_weekday == 4 and display_month == today.month and display_year == today.year %}calendar-weekday--today{% endif %}">Fri</div>
            <div class="calendar-weekday calendar-weekday--weekend {% if current_weekday == 5 and display_month == today.month and display_year == today.year %}calendar-weekday--today{% endif %}">Sat</div>
            <div class="calendar-weekday calendar-weekday--weekend {% if current_weekday == 6 and display_month == today.month and display_year == today.year %}calendar-weekday--today{% endif %}">Sun</div>
        ''')
        
        # Test viewing February 2024 while today is January 15, 2024
        context = Context({
            'current_weekday': 0,  # Monday
            'display_month': 2,    # February (different from today's month)
            'display_year': 2024,
            'today': mock_today
        })
        
        result = template.render(context)
        
        # No weekday should be highlighted
        self.assertNotIn('calendar-weekday--today', result)
    
    def test_weekday_highlighting_different_year(self):
        """Test that weekday headers are NOT highlighted when viewing different year."""
        mock_today = date(2024, 1, 15)  # Monday in January 2024
        
        template = Template('''
            {% load currency_tags %}
            <div class="calendar-weekday {% if current_weekday == 0 and display_month == today.month and display_year == today.year %}calendar-weekday--today{% endif %}">Mon</div>
            <div class="calendar-weekday {% if current_weekday == 1 and display_month == today.month and display_year == today.year %}calendar-weekday--today{% endif %}">Tue</div>
            <div class="calendar-weekday {% if current_weekday == 2 and display_month == today.month and display_year == today.year %}calendar-weekday--today{% endif %}">Wed</div>
            <div class="calendar-weekday {% if current_weekday == 3 and display_month == today.month and display_year == today.year %}calendar-weekday--today{% endif %}">Thu</div>
            <div class="calendar-weekday {% if current_weekday == 4 and display_month == today.month and display_year == today.year %}calendar-weekday--today{% endif %}">Fri</div>
            <div class="calendar-weekday calendar-weekday--weekend {% if current_weekday == 5 and display_month == today.month and display_year == today.year %}calendar-weekday--today{% endif %}">Sat</div>
            <div class="calendar-weekday calendar-weekday--weekend {% if current_weekday == 6 and display_month == today.month and display_year == today.year %}calendar-weekday--today{% endif %}">Sun</div>
        ''')
        
        # Test viewing January 2023 while today is January 15, 2024
        context = Context({
            'current_weekday': 0,  # Monday
            'display_month': 1,    # January (same month)
            'display_year': 2023,  # Different year
            'today': mock_today
        })
        
        result = template.render(context)
        
        # No weekday should be highlighted
        self.assertNotIn('calendar-weekday--today', result)
    
    def test_all_weekdays_highlighting(self):
        """Test highlighting for all weekdays when each is the current day."""
        mock_dates = [
            (date(2024, 1, 15), 0),  # Monday
            (date(2024, 1, 16), 1),  # Tuesday
            (date(2024, 1, 17), 2),  # Wednesday
            (date(2024, 1, 18), 3),  # Thursday
            (date(2024, 1, 19), 4),  # Friday
            (date(2024, 1, 20), 5),  # Saturday
            (date(2024, 1, 21), 6),  # Sunday
        ]
        
        weekday_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        template = Template('''
            {% load currency_tags %}
            <div class="calendar-weekday {% if current_weekday == 0 and display_month == today.month and display_year == today.year %}calendar-weekday--today{% endif %}">Mon</div>
            <div class="calendar-weekday {% if current_weekday == 1 and display_month == today.month and display_year == today.year %}calendar-weekday--today{% endif %}">Tue</div>
            <div class="calendar-weekday {% if current_weekday == 2 and display_month == today.month and display_year == today.year %}calendar-weekday--today{% endif %}">Wed</div>
            <div class="calendar-weekday {% if current_weekday == 3 and display_month == today.month and display_year == today.year %}calendar-weekday--today{% endif %}">Thu</div>
            <div class="calendar-weekday {% if current_weekday == 4 and display_month == today.month and display_year == today.year %}calendar-weekday--today{% endif %}">Fri</div>
            <div class="calendar-weekday calendar-weekday--weekend {% if current_weekday == 5 and display_month == today.month and display_year == today.year %}calendar-weekday--today{% endif %}">Sat</div>
            <div class="calendar-weekday calendar-weekday--weekend {% if current_weekday == 6 and display_month == today.month and display_year == today.year %}calendar-weekday--today{% endif %}">Sun</div>
        ''')
        
        for mock_today, expected_weekday in mock_dates:
            with self.subTest(weekday=weekday_names[expected_weekday]):
                context = Context({
                    'current_weekday': expected_weekday,
                    'display_month': 1,    # January
                    'display_year': 2024,
                    'today': mock_today
                })
                
                result = template.render(context)
                
                # Exactly one weekday should be highlighted
                self.assertEqual(result.count('calendar-weekday--today'), 1)
                
                # The correct weekday should be highlighted
                lines = result.strip().split('\n')
                weekday_line = [line for line in lines if f'{weekday_names[expected_weekday]}</div>' in line][0]
                self.assertIn('calendar-weekday--today', weekday_line)
    
    def test_calendar_grid_template_include(self):
        """Test the actual calendar_grid.html template include."""
        # Read the actual template file
        with open('/home/carlos/dev/projects/python-pyggy-expense-tracker/expenses/templates/expenses/includes/calendar_grid.html', 'r') as f:
            template_content = f.read()
        
        template = Template(template_content)
        
        # Mock today as Wednesday, January 17, 2024
        mock_today = date(2024, 1, 17)
        
        # Test current month view
        context = Context({
            'current_weekday': 2,  # Wednesday
            'display_month': 1,    # January
            'display_year': 2024,
            'today': mock_today,
            'calendar_weeks': [[1, 2, 3, 4, 5, 6, 7], [8, 9, 10, 11, 12, 13, 14]],  # Sample weeks
            'due_days': set(),
        })
        
        result = template.render(context)
        
        # Wednesday should be highlighted
        self.assertIn('calendar-weekday--today', result)
        # Should appear exactly once (only Wednesday)
        wed_count = result.count('calendar-weekday--today')
        self.assertEqual(wed_count, 1)
        
        # Test different month view
        context['display_month'] = 2  # February
        result = template.render(context)
        
        # No weekday should be highlighted
        self.assertEqual(result.count('calendar-weekday--today'), 0)


class DashboardCalendarIntegrationTest(TestCase):
    """Integration test for calendar highlighting in dashboard view."""
    
    def setUp(self):
        """Set up test data."""
        # Clear any existing settings
        Settings.objects.all().delete()
        self.settings = Settings.objects.create(
            locale='en_US',
            currency='USD'
        )
        
        # Create test budget
        self.budget = Budget.objects.create(
            name='Test Budget',
            start_date=date(2024, 1, 1),
            initial_amount=1000.00
        )
        
        self.client = Client()
    
    @patch('expenses.views.date')
    def test_dashboard_calendar_highlighting_current_month(self, mock_date):
        """Test dashboard shows correct weekday highlighting for current month."""
        # Mock today as Wednesday, January 17, 2024
        mock_today = date(2024, 1, 17)
        mock_date.today.return_value = mock_today
        
        # Create a month for January 2024
        month = Month.objects.create(
            month=1,
            year=2024,
            budget=self.budget
        )
        
        response = self.client.get(f'/budgets/{self.budget.id}/dashboard/')
        
        self.assertEqual(response.status_code, 200)
        
        # Check that context contains the right values for highlighting
        self.assertEqual(response.context['current_weekday'], 2)  # Wednesday
        self.assertEqual(response.context['display_month'], 1)    # January
        self.assertEqual(response.context['display_year'], 2024)
        self.assertEqual(response.context['today'], mock_today)
        
        # Check that template contains highlighting logic
        content = response.content.decode()
        self.assertIn('calendar-weekday--today', content)
    
    @patch('expenses.views.date')
    def test_dashboard_calendar_highlighting_different_month(self, mock_date):
        """Test dashboard shows no weekday highlighting when viewing different month."""
        # Mock today as Wednesday, January 17, 2024
        mock_today = date(2024, 1, 17)
        mock_date.today.return_value = mock_today
        
        # Create a month for December 2023 (different from current month)
        month = Month.objects.create(
            month=12,
            year=2023,
            budget=self.budget
        )
        
        response = self.client.get(f'/budgets/{self.budget.id}/dashboard/')
        
        self.assertEqual(response.status_code, 200)
        
        # Context should show December 2023 as display month
        self.assertEqual(response.context['display_month'], 12)   # December
        self.assertEqual(response.context['display_year'], 2023)
        self.assertEqual(response.context['today'], mock_today)   # Still January 17, 2024
        
        # Template should not highlight any weekdays since display month != current month
        content = response.content.decode()
        # Count of weekday highlighting should be 0 in this case
        weekday_today_count = content.count('calendar-weekday--today')
        self.assertEqual(weekday_today_count, 0)