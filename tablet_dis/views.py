from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils.translation import get_language
from django.db.models import Q

from tablet_dis.models import Tablet
from tablet_dis.forms import TabletSearchForm

from tablet_dis.services.db_service import get_tablet_from_db
from tablet_dis.services.save_tablet_service import save_tablet_from_api
from tablet_dis.tablet_checker import (
    check_search_input,
    validate_input_format,
    MEDICINE_NOT_FOUND,
)


# ---------------------------
# Utility: Tamil detection
# ---------------------------
def is_tamil_text(text):
    if not text:
        return False
    return any(0x0B80 <= ord(char) <= 0x0BFF for char in text)


# ---------------------------
# UI Static Texts
# ---------------------------
def _ui_texts(lang):
    if lang == "ta":
        return {
            "label_benefits": "✅ நன்மைகள்",
            "label_side_effects": "⚠️ பக்கவிளைவுகள்",
            "label_dosage": "💊 அளவு & நேரம்",
            "label_age_group": "👥 வயது குழு",
            "label_storage": "📦 சேமிப்பு வழிமுறைகள்",
            "label_interactions": "💊⚠️ மருந்து தொடர்புகள்",
            "disclaimer": "🩺 இந்த தகவல் கல்வி நோக்கங்களுக்காக மட்டுமே. மருந்தை பயன்படுத்தும் முன் மருத்துவரை அணுகவும்.",
            "not_available": "தகவல் இல்லை",
            "consult_doctor_short": "முழு விவரங்களுக்கு மருத்துவரை அணுகவும்.",
        }
    return {
        "label_benefits": "✅ Benefits",
        "label_side_effects": "⚠️ Side effects",
        "label_dosage": "💊 Dosage & Timing",
        "label_age_group": "👥 Age group",
        "label_storage": "📦 Storage instructions",
        "label_interactions": "💊⚠️ Drug interactions",
        "disclaimer": "🩺 This information is for educational purposes only. Consult a doctor before using medicine.",
        "not_available": "Information not available",
        "consult_doctor_short": "Please consult a doctor for full benefits information.",
    }


def _has_content(tablet):
    """True if the tablet has any useful content in English or Tamil."""
    if not tablet:
        return False
    fields = [
        "advantages_en",
        "advantages_ta",
        "disadvantages_en",
        "disadvantages_ta",
        "dosage_timing_en",
        "dosage_timing_ta",
        "interactions_en",
        "interactions_ta",
        "storage_en",
        "storage_ta",
        "age_group_en",
        "age_group_ta",
    ]
    return any(getattr(tablet, f, None) for f in fields)


def _dict_has_content(data):
    if not data:
        return False
    fields = [
        "advantages_en",
        "advantages_ta",
        "disadvantages_en",
        "disadvantages_ta",
        "dosage_timing_en",
        "dosage_timing_ta",
        "interactions_en",
        "interactions_ta",
        "storage_en",
        "storage_ta",
        "age_group_en",
        "age_group_ta",
    ]
    return any(data.get(f) for f in fields)


class TabletObj:
    """Lightweight wrapper for API dict data used in templates."""

    def __init__(self, data):
        for key, value in data.items():
            setattr(self, key, value)

    def get_localized(self, field_base, lang="en"):
        primary = getattr(self, f"{field_base}_{lang}", None)
        if primary and str(primary).strip():
            return primary
        other = "ta" if lang == "en" else "en"
        fallback = getattr(self, f"{field_base}_{other}", None)
        return fallback if fallback and str(fallback).strip() else ""


# ---------------------------
# Home Page
# ---------------------------
def home(request):
    if "language" in request.GET:
        response = redirect("home")
        response.set_cookie("django_language", request.GET["language"])
        return response

    form = TabletSearchForm()
    return render(request, "tablet_dis/home.html", {"form": form})


# ---------------------------
# Tablet Detail Page
# ---------------------------
def tablet_detail(request, name):
    lang = get_language()

    # Tamil auto-detection
    if lang == "en" and is_tamil_text(name):
        lang = "ta"

    texts = _ui_texts(lang)

    # Validate search input
    check = check_search_input(name)
    if not check.ok:
        return render(
            request,
            "tablet_dis/search_message.html",
            {
                "message": check.message,
                "query": name.strip(),
                "page_title": check.message,
            },
        )

    search_name = check.normalized

    # 1️⃣ Try DB first (MODEL)
    tablet = get_tablet_from_db(search_name)

    if tablet and _has_content(tablet):
        display_name = (
            tablet.name_ta if lang == "ta" and tablet.name_ta else tablet.name_en
        )
        return render(
            request,
            "tablet_dis/tablet_detail.html",
            {
                "tablet": tablet,
                "texts": texts,
                "display_name": display_name,
                "lang": lang,
            },
        )

    # 2️⃣ API fallback (DICT)
    api_data = save_tablet_from_api(search_name, lang)

    if api_data and _dict_has_content(api_data):
        tablet_obj = TabletObj(api_data)
        display_name = (
            tablet_obj.name_ta
            if lang == "ta" and getattr(tablet_obj, "name_ta", "")
            else getattr(tablet_obj, "name_en", name)
        )
        return render(
            request,
            "tablet_dis/tablet_detail.html",
            {
                "tablet": tablet_obj,
                "texts": texts,
                "display_name": display_name,
                "lang": lang,
            },
        )

    # 3️⃣ DB row exists but API failed/empty — still show DB data
    if tablet:
        display_name = (
            tablet.name_ta if lang == "ta" and tablet.name_ta else tablet.name_en
        )
        return render(
            request,
            "tablet_dis/tablet_detail.html",
            {
                "tablet": tablet,
                "texts": texts,
                "display_name": display_name,
                "lang": lang,
            },
        )

    return render(
        request,
        "tablet_dis/search_message.html",
        {
            "message": MEDICINE_NOT_FOUND,
            "query": search_name,
            "page_title": MEDICINE_NOT_FOUND,
        },
    )


# ---------------------------
# Search validation API (for search bar)
# ---------------------------
def validate_search(request):
    query = request.GET.get("q", "")
    result = validate_input_format(query)
    return JsonResponse(
        {
            "ok": result.ok,
            "message": result.message,
            "normalized": result.normalized,
        }
    )


# ---------------------------
# Autocomplete API
# ---------------------------
def autocomplete(request):
    query = request.GET.get("q", "").strip()
    lang = get_language()

    if is_tamil_text(query):
        lang = "ta"

    if len(query) < 2:
        return JsonResponse([], safe=False)

    check = validate_input_format(query)
    if not check.ok:
        return JsonResponse([], safe=False)

    tablets = Tablet.objects.filter(
        Q(name_en__icontains=query) | Q(name_ta__icontains=query)
    )[:10]

    suggestions = []
    for tablet in tablets:
        name = tablet.name_ta if lang == "ta" and tablet.name_ta else tablet.name_en
        if name and name not in suggestions:
            suggestions.append(name)

    return JsonResponse(suggestions, safe=False)
