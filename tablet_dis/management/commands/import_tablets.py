import csv
from django.core.management.base import BaseCommand
from tablet_dis.models import Tablet

class Command(BaseCommand):
    help = 'Import tablets from a CSV file containing bilingual data.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        with open(options['csv_file'], encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                Tablet.objects.update_or_create(
                    name_en=row['name_en'],
                    defaults={
                        'name_ta': row.get('name_ta', ''),
                        'advantages_en': row['advantages_en'],
                        'advantages_ta': row.get('advantages_ta', ''),
                        'disadvantages_en': row['disadvantages_en'],
                        'disadvantages_ta': row.get('disadvantages_ta', ''),
                        'dosage_timing_en': row['dosage_timing_en'],
                        'dosage_timing_ta': row.get('dosage_timing_ta', ''),
                        'age_group_en': row['age_group_en'],
                        'age_group_ta': row.get('age_group_ta', ''),
                    }
                )
                count += 1
            self.stdout.write(self.style.SUCCESS(f'Imported {count} tablets.'))
