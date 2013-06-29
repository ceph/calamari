from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stderr.write("for real refresh not yet implemented...")
