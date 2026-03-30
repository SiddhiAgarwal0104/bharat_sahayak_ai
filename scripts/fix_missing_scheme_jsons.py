# scripts/fix_missing_scheme_jsons.py
# Finds schemes in MongoDB that have no matching form JSON, then creates one.

import json, glob, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.database import get_schemes_collection

col = get_schemes_collection()

# Get all scheme_ids that already have JSON files
existing_json_ids = set()
for path in glob.glob("data/forms/*.json"):
    fname = os.path.basename(path).replace(".json", "")
    if len(fname) == 24:
        existing_json_ids.add(fname)

print(f"JSON files already covering {len(existing_json_ids)} scheme IDs\n")

# Find schemes with no JSON
missing = []
for s in col.find({}, {"_id": 1, "name": 1, "category": 1}):
    sid = str(s["_id"])
    if sid not in existing_json_ids:
        missing.append(s)
        print(f"  MISSING JSON: {sid} | {s['name']}")

if not missing:
    print("All schemes already have JSON files!")
    sys.exit(0)

print(f"\nCreating {len(missing)} missing JSON files...\n")

# Default fields template per category
def make_fields(category):
    base = [
        {
            "field_id": 1, "field_name": "Applicant Name", "field_type": "text",
            "required": True, "can_prefill": True, "prefill_source": "user.name",
            "instruction_en": "Enter your full name as per Aadhaar card.",
            "instruction_hi": "अपना पूरा नाम आधार कार्ड के अनुसार लिखें।",
            "document_needed": "Aadhaar Card", "validation": None
        },
        {
            "field_id": 2, "field_name": "Date of Birth", "field_type": "date",
            "required": True, "can_prefill": True, "prefill_source": "user.age",
            "instruction_en": "Enter your date of birth in DD/MM/YYYY format.",
            "instruction_hi": "जन्म तिथि DD/MM/YYYY प्रारूप में दर्ज करें।",
            "document_needed": "Aadhaar Card", "validation": None
        },
        {
            "field_id": 3, "field_name": "Gender", "field_type": "dropdown",
            "required": True, "can_prefill": True, "prefill_source": "user.gender",
            "instruction_en": "Select your gender.",
            "instruction_hi": "अपना लिंग चुनें।",
            "document_needed": None, "validation": None
        },
        {
            "field_id": 4, "field_name": "Address", "field_type": "text",
            "required": True, "can_prefill": True, "prefill_source": "user.location",
            "instruction_en": "Enter your full residential address including district and state.",
            "instruction_hi": "अपना पूरा पता दर्ज करें — जिला और राज्य सहित।",
            "document_needed": "Aadhaar Card or Voter ID", "validation": None
        },
        {
            "field_id": 5, "field_name": "Mobile Number", "field_type": "text",
            "required": True, "can_prefill": False, "prefill_source": None,
            "instruction_en": "Enter your 10-digit mobile number linked to Aadhaar.",
            "instruction_hi": "आधार से जुड़ा 10 अंकों का मोबाइल नंबर दर्ज करें।",
            "document_needed": None, "validation": "10 digits"
        },
    ]

    extra = {
        "agriculture": [
            {
                "field_id": 6, "field_name": "Land Holding (in acres)", "field_type": "text",
                "required": True, "can_prefill": False, "prefill_source": None,
                "instruction_en": "Enter total agricultural land you own in acres. Include survey number.",
                "instruction_hi": "अपनी कृषि भूमि एकड़ में दर्ज करें। सर्वे नंबर भी लिखें।",
                "document_needed": "Khasra / Land Records (Bhulekh)", "validation": None
            },
            {
                "field_id": 7, "field_name": "Bank Account Number", "field_type": "text",
                "required": True, "can_prefill": False, "prefill_source": None,
                "instruction_en": "Enter your bank account number for subsidy credit.",
                "instruction_hi": "सब्सिडी के लिए अपना बैंक खाता नंबर दर्ज करें।",
                "document_needed": "Bank Passbook", "validation": None
            },
        ],
        "health": [
            {
                "field_id": 6, "field_name": "Annual Family Income", "field_type": "text",
                "required": True, "can_prefill": True, "prefill_source": "user.annual_income",
                "instruction_en": "Enter your total annual family income in rupees.",
                "instruction_hi": "परिवार की कुल वार्षिक आय रुपयों में दर्ज करें।",
                "document_needed": "Income Certificate", "validation": None
            },
            {
                "field_id": 7, "field_name": "Ration Card Number", "field_type": "text",
                "required": False, "can_prefill": False, "prefill_source": None,
                "instruction_en": "Enter your ration card number if available (BPL/AAY preferred).",
                "instruction_hi": "राशन कार्ड नंबर दर्ज करें यदि उपलब्ध हो।",
                "document_needed": "Ration Card", "validation": None
            },
        ],
        "pension": [
            {
                "field_id": 6, "field_name": "Employment Type", "field_type": "dropdown",
                "required": True, "can_prefill": False, "prefill_source": None,
                "instruction_en": "Select whether you are a government or private sector employee.",
                "instruction_hi": "चुनें — सरकारी या निजी क्षेत्र का कर्मचारी।",
                "document_needed": "Employment Certificate", "validation": None
            },
            {
                "field_id": 7, "field_name": "Bank Account Number", "field_type": "text",
                "required": True, "can_prefill": False, "prefill_source": None,
                "instruction_en": "Enter bank account number for pension credit.",
                "instruction_hi": "पेंशन के लिए बैंक खाता नंबर दर्ज करें।",
                "document_needed": "Bank Passbook", "validation": None
            },
        ],
        "women": [
            {
                "field_id": 6, "field_name": "Marital Status", "field_type": "dropdown",
                "required": True, "can_prefill": False, "prefill_source": None,
                "instruction_en": "Select your marital status.",
                "instruction_hi": "अपनी वैवाहिक स्थिति चुनें।",
                "document_needed": None, "validation": None
            },
            {
                "field_id": 7, "field_name": "Annual Income", "field_type": "text",
                "required": True, "can_prefill": True, "prefill_source": "user.annual_income",
                "instruction_en": "Enter your annual household income in rupees.",
                "instruction_hi": "वार्षिक घरेलू आय रुपयों में दर्ज करें।",
                "document_needed": "Income Certificate", "validation": None
            },
        ],
    }

    return base + extra.get(category, [])

for s in missing:
    sid = str(s["_id"])
    name = s["name"]
    category = s.get("category", "other")

    json_data = {
        "scheme_id": sid,
        "scheme_name": name,
        "form_url": "https://www.myscheme.gov.in",
        "fields": make_fields(category)
    }

    out_path = f"data/forms/{sid}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    print(f"  Created: {sid}.json ({name}, {len(json_data['fields'])} fields)")

print(f"\nDone. Now run: python scripts/seed_forms.py")