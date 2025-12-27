# tablet_dis/services/db_service.py

from tablet_dis.models import Tablet
from django.db.models import Q


def get_tablet_from_db(name):
    """
    Fetch tablet data from DB using partial match (safe & flexible)
    """
    return (
        Tablet.objects.filter(
            Q(name_en__icontains=name) |
            Q(name_ta__icontains=name)
        )
        .order_by("id")
        .first()
    )
