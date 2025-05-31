from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Load initial data for the expense tracker'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Loading initial data...'))
        
        try:
            call_command('loaddata', 'fixtures/initial_data.json')
            self.stdout.write(
                self.style.SUCCESS('Successfully loaded initial data!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error loading initial data: {e}')
            )