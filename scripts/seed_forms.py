# scripts/seed_forms.py
import json, glob, sys, os, asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from backend.config import settings
from backend.models.form_field import FormField

async def seed():
    client = AsyncIOMotorClient(settings.MONGO_URL)
    db = client[settings.MONGO_DB]
    await init_beanie(database=db, document_models=[FormField])

    # Clear existing
    deleted = await FormField.find_all().delete()
    print(f"Cleared existing form fields.")

    json_files = glob.glob("data/forms/*.json")
    if not json_files:
        print("ERROR: No JSON files found in data/forms/")
        return

    print(f"Found {len(json_files)} form JSON files")
    total = 0

    for path in sorted(json_files):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        scheme_id = data.get("scheme_id")
        fields = data.get("fields", [])

        if not scheme_id or not fields:
            print(f"  Skipping {path} — missing scheme_id or fields")
            continue

        print(f"  Seeding {scheme_id}: {len(fields)} fields")

        for field in fields:
            doc = FormField(
                scheme_id       = scheme_id,
                field_id        = field["field_id"],
                field_name      = field["field_name"],
                field_type      = field["field_type"],
                required        = field.get("required", True),
                can_prefill     = field.get("can_prefill", False),
                prefill_source  = field.get("prefill_source"),
                instruction_en  = field["instruction_en"],
                instruction_hi  = field["instruction_hi"],
                document_needed = field.get("document_needed"),
                validation      = field.get("validation"),
            )
            await doc.insert()
            total += 1

    print(f"Done! Seeded {total} form fields total.")
    client.close()

if __name__ == "__main__":
    asyncio.run(seed())