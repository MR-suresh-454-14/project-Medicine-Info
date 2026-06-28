from tablet_dis.models import Tablet
from tablet_dis.services.openai_service import scrape_tablet_details
from django.db import IntegrityError


def save_tablet_from_api(tablet_name, user_language="en"):
    """
    Call OpenAI API, return data for UI,
    and save data into DB if not already present.
    """

    # 🔹 Call OpenAI service
    api_data = scrape_tablet_details(tablet_name, user_language)

    if not api_data:
        return None

    name_en = api_data.get("name_en", "").strip()
    name_ta = api_data.get("name_ta", "").strip()

    # 🔹 Safety check (DB NOT NULL fields)
    if not name_en:
        name_en = tablet_name

    try:
        # 🔹 Save only if not exists
        tablet, created = Tablet.objects.get_or_create(
            name_en=name_en,
            defaults={
                "name_ta": name_ta,
                "advantages_en": api_data.get("advantages_en", ""),
                "advantages_ta": api_data.get("advantages_ta", ""),
                "disadvantages_en": api_data.get("disadvantages_en", ""),
                "disadvantages_ta": api_data.get("disadvantages_ta", ""),
                "dosage_timing_en": api_data.get("dosage_timing_en", ""),
                "dosage_timing_ta": api_data.get("dosage_timing_ta", ""),
                "age_group_en": api_data.get("age_group_en", ""),
                "age_group_ta": api_data.get("age_group_ta", ""),
                "storage_en": api_data.get("storage_en", ""),
                "storage_ta": api_data.get("storage_ta", ""),
                "interactions_en": api_data.get("interactions_en", ""),
                "interactions_ta": api_data.get("interactions_ta", ""),
            }
        )

        # 🔹 If record already exists, update any missing fields from API
        if not created:
            updated_fields = []
            # Ensure Tamil name is set
            if name_ta and not tablet.name_ta:
                tablet.name_ta = name_ta
                updated_fields.append("name_ta")

            # Update other blank fields from api_data
            field_names = [
                "advantages_en",
                "advantages_ta",
                "disadvantages_en",
                "disadvantages_ta",
                "dosage_timing_en",
                "dosage_timing_ta",
                "age_group_en",
                "age_group_ta",
                "storage_en",
                "storage_ta",
                "interactions_en",
                "interactions_ta",
            ]

            for fn in field_names:
                api_val = api_data.get(fn, "")
                if api_val and not getattr(tablet, fn, None):
                    setattr(tablet, fn, api_val)
                    updated_fields.append(fn)

            if updated_fields:
                tablet.save(update_fields=updated_fields)

        # 🔹 Return data for UI (not model)
        return api_data

    except IntegrityError:
        # DB constraint issue → still show API data
        return api_data
