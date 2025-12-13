from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils.translation import get_language
from django.db.models import Q
from .models import Tablet
from .forms import TabletSearchForm
from .scraper import scrape_tablet_details
import unicodedata  # for Tamil detection


def is_tamil_text(text):
    """
    Detect if input contains Tamil characters
    Tamil Unicode block: 0B80–0BFF
    """
    if not text:
        return False
    tamil_range = range(0x0B80, 0x0BFF)
    return any(ord(char) in tamil_range for char in text)


def _ui_texts(lang):
    """
    Provide UI static texts depending on language.
    """
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


def home(request):
    """Home page with language switch + search form"""
    if "language" in request.GET:
        response = redirect("home")
        response.set_cookie("django_language", request.GET["language"])
        return response
    form = TabletSearchForm()
    return render(request, "tablet_dis/home.html", {"form": form})


def tablet_detail(request, name):
    lang = get_language()  # 'en' or 'ta'
    if lang == 'en' and is_tamil_text(name):
        lang = 'ta'

    # Fetch tablet data (from scraper, returns dict)
    tablet_data = scrape_tablet_details(name, user_language=lang)

    class TabletObj:
        def __init__(self, data):
            for k, v in data.items():
                setattr(self, k, v)

    tablet = TabletObj(tablet_data)
    texts = _ui_texts(lang)
    display_name = tablet_data.get("name_ta") if lang == "ta" and tablet_data.get("name_ta") else tablet_data.get("name_en", name)

    context = {
        "tablet": tablet,
        "texts": texts,
        "display_name": display_name,
    }
    return render(request, "tablet_dis/tablet_detail.html", context)


def autocomplete(request):
    """Autocomplete suggestions with Tamil detection"""
    query = request.GET.get("q", "").strip()
    lang = get_language()

    if is_tamil_text(query):
        lang = "ta"

    if len(query) < 2:
        return JsonResponse([], safe=False)

    tablets = Tablet.objects.filter(Q(name_en__icontains=query) | Q(name_ta__icontains=query))[:10]

    suggestions = []
    for tablet in tablets:
        suggestion = tablet.name_ta if lang == "ta" and tablet.name_ta else tablet.name_en
        if suggestion and suggestion not in suggestions:
            suggestions.append(suggestion)

    return JsonResponse(suggestions, safe=False)
