import os
import requests
import json

# Test the API call directly
api_key = os.getenv('OPENROUTER_API_KEY')
print(f"API Key found: {api_key is not None}")

url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost:8000",
    "X-Title": "Tablet Information System"
}

data = {
    "model": "openai/gpt-3.5-turbo",
    "messages": [
        {
            "role": "system",
            "content": "You are a medical information generator. Return ONLY a valid JSON object. No explanations, no code fences, no markdown."
        },
        {
            "role": "user", 
            "content": 'Provide accurate medical information about "aspirin" as a JSON object with these exact keys: {"name_en": "...", "benefits_en": "...", "side_effects_en": "...", "dosage_en": "...", "age_group_en": "..."}'
        }
    ],
    "temperature": 0.3,
    "max_tokens": 800
}

try:
    print("Making API call...")
    response = requests.post(url, headers=headers, json=data, timeout=30)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        content = result['choices'][0]['message']['content'].strip()
        print("API Response:")
        print(content)
        
        # Try to parse as JSON
        try:
            parsed = json.loads(content)
            print("✅ JSON parsed successfully!")
            print("Name:", parsed.get('name_en'))
            print("Benefits:", parsed.get('benefits_en', '')[:50] + "...")
        except json.JSONDecodeError:
            print("❌ Failed to parse JSON")
    else:
        print("❌ API call failed")
        print("Response:", response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")