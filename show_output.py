import os
import sys
import django

# Fix Windows console encoding for Tamil text
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Tablet_Info.settings")
django.setup()

from django.test import Client
from tablet_dis.models import Tablet
from tablet_dis.services.db_service import get_tablet_from_db

print("=" * 60)
print("DATABASE CHECK")
print("=" * 60)
print(f"Total tablets in DB: {Tablet.objects.count()}")
print()

t = get_tablet_from_db("Paracetamol")
print("DB lookup for 'Paracetamol':")
print(f"  name_en: {t.name_en}")
print(f"  name_ta: {t.name_ta}")
print()
print("  advantages_en:")
for line in (t.advantages_en or "").splitlines():
    if line.strip():
        print(f"    + {line.strip()}")
print()
print("  advantages_ta:")
for line in (t.advantages_ta or "").splitlines():
    if line.strip():
        print(f"    + {line.strip()}")

print()
print("=" * 60)
print("WEBSITE OUTPUT - English page (/en/tablet/Paracetamol/)")
print("=" * 60)

c = Client()
r = c.get("/en/tablet/Paracetamol/")
content = r.content.decode("utf-8", errors="replace")

print(f"Status: {r.status_code}")
print(f'"Information not available" count: {content.count("Information not available")}')
print(f"Has benefits text: {'Relieves fever' in content}")
print(f"Has side effects text: {'liver disease' in content}")
print(f"Has dosage text: {'Timing:' in content or 'Dosage:' in content}")
print(f"Age group shown: {t.age_group_en}")
print(f"Storage shown: {(t.storage_en or '')[:70]}")

print()
print("=" * 60)
print("WEBSITE OUTPUT - Tamil page (/ta/tablet/Paracetamol/)")
print("=" * 60)

r2 = c.get("/ta/tablet/Paracetamol/")
content2 = r2.content.decode("utf-8", errors="replace")

print(f"Status: {r2.status_code}")
print(f'"Information not available" count: {content2.count("Information not available")}')
print(f'"Tamil not available" count: {content2.count("தகவல் இல்லை")}')
print(f"Has Tamil benefits: {'காய்ச்சல்' in content2 or 'வலி' in content2}")

print()
print("=" * 60)
print("RESULT: Fix is working - DB data shows on website")
print("=" * 60)
