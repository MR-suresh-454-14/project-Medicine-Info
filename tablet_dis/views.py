from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils.translation import get_language
from django.db.models import Q

from tablet_dis.models import Tablet
from tablet_dis.forms import TabletSearchForm

from tablet_dis.services.db_service import get_tablet_from_db
from tablet_dis.services.save_tablet_service import save_tablet_from_api

import unicodedata


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

    # 1️⃣ Try DB first (MODEL)
    tablet = get_tablet_from_db(name)

    if tablet and hasattr(tablet, "name_en"):
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
            },
        )

    # 2️⃣ API fallback (DICT)
    api_data = save_tablet_from_api(name, lang)

    if not api_data:
        return render(
            request,
            "tablet_dis/tablet_detail.html",
            {
                "tablet": None,
                "texts": texts,
                "display_name": name,
            },
        )

    # ✅ Convert dict → object (IMPORTANT)
    class TabletObj:
        pass

    tablet_obj = TabletObj()
    for k, v in api_data.items():
        setattr(tablet_obj, k, v)

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
        },
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

    tablets = Tablet.objects.filter(
        Q(name_en__icontains=query) | Q(name_ta__icontains=query)
    )[:10]

    suggestions = []
    for tablet in tablets:
        name = tablet.name_ta if lang == "ta" and tablet.name_ta else tablet.name_en
        if name and name not in suggestions:
            suggestions.append(name)

    return JsonResponse(suggestions, safe=False)
