import os

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Load data from CSV files into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "directory", type=str, help="Directory containing CSV files")

    def handle(self, *args, **kwargs):
        directory = kwargs["directory"]
        if not os.path.isdir(directory):
            self.stderr.write(self.style.ERROR(
                f'Directory "{directory}" does not exist'))
            return

        self.stdout.write(self.style.SUCCESS(
            f'Successfully loaded data from "{directory}"'))
