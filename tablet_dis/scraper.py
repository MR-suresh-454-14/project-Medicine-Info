# this main script in the project 
import os
import json
import logging
import requests

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

def build_messages(tablet_name, user_language):
    tamil_prompt = f"""
பின்வரும் மருந்து "{tablet_name}" பற்றி தெளிவாகவும் எளிமையாகவும் மருத்துவ தகவல் கொடு.
JSON வடிவில் இவ்வாறு திருப்பவும்:
{{
  "name_en": "...", "name_ta": "...",
  "benefits_en": "...", "benefits_ta": "...",
  "side_effects_en": "...", "side_effects_ta": "...",
  "dosage_en": "...", "dosage_ta": "...",
  "age_group_en": "...", "age_group_ta": "...",
  "storage_en": "...", "storage_ta": "...",
  "interactions_en": "...", "interactions_ta": "..."
}}
# "tamil prompt and you can change here"

# நன்மைகள்
benefits_ta: சரியாக 4–6 வரிகள். ஒவ்வொரு வரியும் ஒரு முழு புள்ளி மட்டும்.
பட்டியலை newline மூலம் மட்டும் பிரிக்கவும்.
ஒரே வரியில் ஒரு புள்ளி மட்டுமே. நீளமான வாக்கியங்கள் வேண்டாம்.

# பக்கவிளைவுகள்
side_effects_ta: சரியாக 4–6 வரிகள், ஒவ்வொரு வரியிலும் ஒரு புள்ளி மட்டும்.
முதல் வரி ‘எடுத்துக்கொள்ளக்கூடாதவர்கள்: …’ என்ற வடிவில் இருக்க வேண்டும்.
இரண்டாவது வரி ‘நீண்ட நேரம் தொடர்ச்சியாக எடுத்தால் …’ என்று தொடங்க வேண்டும்.
வரிகள் newline மூலம் மட்டும் பிரிக்கப்பட வேண்டும்.

# அளவு மற்றும் நேரம்
dosage_ta: இரண்டு வரிகள்.
முதல் வரி 'நேரம்:' என்று தொடங்கி எப்போது எடுத்தால் சரியாகும் என்று குறிப்பிடவும்.
இரண்டாவது வரி 'அளவு:' என்று தொடங்கி பெரியவர்கள் மற்றும் குழந்தைகளுக்கு அளவு கூறவும்.

# வயது குழு
age_group_ta: எளிய வார்த்தைகளில், உதா: 'பெரியவர்கள் மட்டும்', '6 வயது மேல் குழந்தைகள்'.

# சேமிப்பு
storage_ta: 1–2 வரிகள். உதா: 'குளிர்ந்த, உலர் இடத்தில் சேமிக்கவும். குழந்தைகளுக்கு வெளியே வைக்கவும்.'

# மருந்து தொடர்புகள்
interactions_ta: 2–3 வரிகள். உதா: 'மதுபானத்துடன் எடுக்க வேண்டாம்', 'மற்ற வலியினை குறைக்கும் மருந்துகளுடன் சேர்க்க வேண்டாம்'

# முக்கியம்
JSON மட்டுமே திருப்பவும். விளக்கங்கள், மார்க்டவுன் எந்தவையும் சேர்க்க வேண்டாம்.
"""


    english_prompt = f"""
Provide clear and simple medical information about "{tablet_name}" as a JSON object:
{{
  "name_en": "...", "name_ta": "...",
  "benefits_en": "...", "benefits_ta": "...",
  "side_effects_en": "...", "side_effects_ta": "...",
  "dosage_en": "...", "dosage_ta": "...",
  "age_group_en": "...", "age_group_ta": "...",
  "storage_en": "...", "storage_ta": "...",
  "interactions_en": "...", "interactions_ta": "..."
}}
# "english prompt and you can change here"

# Benefits
benefits_en: exactly 4–6 lines, one short point per line.
Separate items by newline only. Do not use paragraphs or commas.

# Side Effects
side_effects_en: exactly 4–6 lines, one point per line.
First line: "Who should NOT take: …".
Second line must start with "If taken continuously for a long time, …".
Separate strictly by newline only.

# Dosage & Timing
dosage_en: two lines.
First line starts "Timing:" indicating when to take it.
Second line starts "Dosage:" with adult and child amounts.

# Age Group
age_group_en: simple words like "Adults only", "Children above 6 years".

# Storage
storage_en: 1–2 lines like "Store in cool dry place away from sunlight. Keep away from children."

# Drug Interactions
interactions_en: 2–3 lines like "Do not take with alcohol", "Avoid combining with other painkillers."

Return ONLY the JSON object. No explanations, no markdown.
"""


    if user_language == "ta":
        user_content = tamil_prompt
    else:
        user_content = english_prompt

    return [
        {"role": "system", "content": "You are a medical information assistant. Provide accurate, detailed answers about medicines in JSON format only."},
        {"role": "user", "content": user_content}
    ]


def call_models_for_json(messages):
    if not API_KEY:
        logger.error("OPENROUTER_API_KEY environment variable not set")
        return None

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openai/gpt-4o-mini",
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 3000,
        "response_format": {"type": "json_object"}
    }

    logger.debug(f"Sending API request: {json.dumps(data, ensure_ascii=False)}")
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        resp_json = response.json()
        content = resp_json["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as e:
        logger.error(f"API call failed: {e}", exc_info=True)
        return None

def rename_api_keys(api_data):
    return {
        "name_en": api_data.get("name_en", ""),
        "name_ta": api_data.get("name_ta", ""),
        "advantages_ta": api_data.get("benefits_ta", ""),
        "advantages_en": api_data.get("benefits_en", ""),
        "disadvantages_ta": api_data.get("side_effects_ta", ""),
        "disadvantages_en": api_data.get("side_effects_en", ""),
        "dosage_timing_ta": api_data.get("dosage_ta", ""),
        "dosage_timing_en": api_data.get("dosage_en", ""),
        "age_group_ta": api_data.get("age_group_ta", ""),
        "age_group_en": api_data.get("age_group_en", ""),
        "storage_ta": api_data.get("storage_ta", ""),
        "storage_en": api_data.get("storage_en", ""),
        "interactions_ta": api_data.get("interactions_ta", ""),
        "interactions_en": api_data.get("interactions_en", "")
    }

def fallback_data(tablet_name, user_language):
    return {
        "name_en": tablet_name,
        "name_ta": tablet_name if user_language == "ta" else "",
        "advantages_en": "",
        "advantages_ta": "",
        "disadvantages_en": "",
        "disadvantages_ta": "",
        "dosage_timing_en": "",
        "dosage_timing_ta": "",
        "age_group_en": "",
        "age_group_ta": "",
        "storage_en": "",
        "storage_ta": "",
        "interactions_en": "",
        "interactions_ta": "",
    }

def scrape_tablet_details(tablet_name, user_language="en"):
    messages = build_messages(tablet_name, user_language)
    api_response = call_models_for_json(messages)
    if api_response:
        return rename_api_keys(api_response)
    return fallback_data(tablet_name, user_language)