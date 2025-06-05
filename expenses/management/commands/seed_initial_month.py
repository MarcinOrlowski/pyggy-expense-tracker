from django.core.management.base import BaseCommand
from django.db import transaction
from expenses.models import Month, Budget
from expenses.services import process_new_month


class Command(BaseCommand):
    help = 'Seeds the system with an initial month'

    def add_arguments(self, parser):
        parser.add_argument(
            '--year',
            type=int,
            default=2025,
            help='Year for the initial month (default: 2025)'
        )
        parser.add_argument(
            '--month',
            type=int,
            default=1,
            help='Month for the initial month (default: 1)'
        )

    def handle(self, *args, **options):
        year = options['year']
        month = options['month']
        
        # Check if any months already exist
        if Month.objects.exists():
            self.stdout.write(
                self.style.ERROR(
                    'Months already exist in the system. Initial seeding is not allowed.'
                )
            )
            return
        
        # Validate year and month
        if not (2020 <= year <= 2099):
            self.stdout.write(
                self.style.ERROR('Year must be between 2020 and 2099')
            )
            return
        
        if not (1 <= month <= 12):
            self.stdout.write(
                self.style.ERROR('Month must be between 1 and 12')
            )
            return
        
        try:
            with transaction.atomic():
                # Get or create a default budget
                budget, created = Budget.objects.get_or_create(
                    defaults={'name': 'Default Budget', 'description': 'Default budget for initial setup'}
                )
                month_obj = process_new_month(year, month, budget)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully seeded initial month: {month_obj}'
                    )
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error seeding initial month: {str(e)}')
            )