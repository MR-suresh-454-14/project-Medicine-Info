import csv
from django.core.management.base import BaseCommand
from tablet_dis.models import Tablet

class Command(BaseCommand):
    help = "Import tablets from CSV file"

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        csv_file = options['csv_file']

        with open(csv_file, encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)

            for row in reader:
                if not row.get('name_en'):
                    continue  # skip broken rows safely

                Tablet.objects.create(
                    name_en=row['name_en'].strip(),
                    name_ta=row.get('name_ta', '').strip(),

                    advantages_en=row.get('advantages_en', ''),
                    advantages_ta=row.get('advantages_ta', ''),

                    disadvantages_en=row.get('disadvantages_en', ''),
                    disadvantages_ta=row.get('disadvantages_ta', ''),

                    dosage_timing_en=row.get('dosage_timing_en', ''),
                    dosage_timing_ta=row.get('dosage_timing_ta', ''),

                    age_group_en=row.get('age_group_en', ''),
                    age_group_ta=row.get('age_group_ta', ''),

                    storage_en=row.get('storage_en', ''),
                    storage_ta=row.get('storage_ta', ''),

                    interactions_en=row.get('interactions_en', ''),
                    interactions_ta=row.get('interactions_ta', ''),
                )

        self.stdout.write(self.style.SUCCESS("CSV import completed"))
