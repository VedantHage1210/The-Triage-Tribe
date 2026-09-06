"""
Seed script — Day 2 deliverable. Run with: python -m scripts.seed_data
Populates symptoms_i18n, ui_content_i18n, and a starter knowledge_base
(Section 8.2 — replace/expand these with real dataset rows once you've
downloaded the Disease-Symptom DB / ICD-10 data).
"""
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.models import KnowledgeBase, Symptom, UIContent

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# --- symptoms_i18n (Section 5.1) ----------------------------------------
SYMPTOMS = [
    # code, label_en, label_de, category, red_flag
    ("chest_pain", "Chest pain", "Brustschmerzen", "heart", True),
    ("shortness_of_breath", "Shortness of breath", "Atemnot", "heart", True),
    ("unconscious", "Loss of consciousness", "Bewusstlosigkeit", "general", True),
    ("severe_bleeding", "Severe bleeding", "Starke Blutung", "general", True),
    ("slurred_speech", "Slurred speech", "Undeutliche Sprache", "general", True),
    ("mild_headache", "Mild headache", "Leichte Kopfschmerzen", "general", False),
    ("sore_throat", "Sore throat", "Halsschmerzen", "general", False),
    ("eye_redness", "Eye redness", "Rote Augen", "eyes", False),
    ("blurred_vision", "Blurred vision", "Verschwommenes Sehen", "eyes", False),
    ("eye_pain", "Eye pain", "Augenschmerzen", "eyes", False),
    ("skin_rash", "Skin rash", "Hautausschlag", "skin", False),
    ("itching", "Itching", "Juckreiz", "skin", False),
    ("tooth_pain", "Tooth pain", "Zahnschmerzen", "teeth", False),
    ("bleeding_gums", "Bleeding gums", "Zahnfleischbluten", "teeth", False),
    ("nausea", "Nausea", "Übelkeit", "digestion", False),
    ("abdominal_pain", "Abdominal pain", "Bauchschmerzen", "digestion", False),
    ("excessive_thirst", "Excessive thirst", "Übermäßiger Durst", "diabetes", False),
    ("frequent_urination", "Frequent urination", "Häufiges Wasserlassen", "diabetes", False),
    ("unexplained_weight_loss", "Unexplained weight loss", "Unerklärlicher Gewichtsverlust", "weight", False),
    ("fatigue", "Fatigue", "Müdigkeit", "general", False),
]

for code, en, de, category, red_flag in SYMPTOMS:
    if not db.query(Symptom).filter_by(code=code).first():
        db.add(Symptom(code=code, label_en=en, label_de=de, category=category, red_flag=red_flag))

# --- ui_content_i18n (Section 5.4) --------------------------------------
UI_CONTENT = [
    ("disclaimer_banner",
     "This tool provides decision support and is not a medical diagnosis. "
     "If this is a medical emergency, call your local emergency number immediately.",
     "Dieses Tool bietet Entscheidungsunterstützung und stellt keine medizinische "
     "Diagnose dar. Rufen Sie im Notfall sofort den lokalen Notdienst an."),
    ("landing_title", "AI-Powered Clinical Triage Assistant", "KI-gestützter klinischer Triage-Assistent"),
    ("landing_subtitle", "Describe your symptoms and get guidance on the right next step.",
     "Beschreiben Sie Ihre Symptome und erhalten Sie Hinweise zum richtigen nächsten Schritt."),
    ("start_button", "Start Assessment", "Bewertung starten"),
    ("loading_message", "Analyzing your symptoms...", "Ihre Symptome werden analysiert..."),
    ("download_report_button", "Download Report (PDF)", "Bericht herunterladen (PDF)"),
    ("observation_disclaimer",
     "AI Visual Observation — Not a Diagnosis. This is a general observation only; "
     "please consult a specialist for an accurate assessment.",
     "KI-Sichtbeobachtung — Keine Diagnose. Dies ist nur eine allgemeine Beobachtung; "
     "bitte konsultieren Sie einen Facharzt für eine genaue Beurteilung."),
]

for key, en, de in UI_CONTENT:
    if not db.query(UIContent).filter_by(key=key).first():
        db.add(UIContent(key=key, value_en=en, value_de=de))

# --- knowledge_base starter rows (Section 8.2 — expand with real dataset) --
KNOWLEDGE_BASE = [
    {
        "condition_name": "Conjunctivitis",
        "icd_code": "H10",
        "category": "eyes",
        "associated_symptoms": ["eye redness", "eye pain", "itching", "discharge"],
        "typical_severity": "ROUTINE",
        "guidance_text_en": "Often resolves on its own; keep the eye clean and avoid touching it. "
                             "See a doctor if pain is severe or vision is affected.",
        "guidance_text_de": "Heilt oft von selbst; Auge sauber halten und nicht berühren. "
                             "Bei starken Schmerzen oder Sehstörungen einen Arzt aufsuchen.",
        "source_dataset": "Disease-Symptom Knowledge Database",
    },
    {
        "condition_name": "Acute Angina",
        "icd_code": "I20",
        "category": "heart",
        "associated_symptoms": ["chest pain", "shortness of breath", "sweating"],
        "typical_severity": "EMERGENCY",
        "guidance_text_en": "Chest pain with shortness of breath can indicate a cardiac emergency. "
                             "Seek emergency care immediately.",
        "guidance_text_de": "Brustschmerzen mit Atemnot können auf einen kardialen Notfall hinweisen. "
                             "Sofort einen Notarzt aufsuchen.",
        "source_dataset": "Disease-Symptom Knowledge Database",
    },
    {
        "condition_name": "Contact Dermatitis",
        "icd_code": "L23",
        "category": "skin",
        "associated_symptoms": ["skin rash", "itching", "redness"],
        "typical_severity": "SELF_CARE",
        "guidance_text_en": "Usually caused by an irritant or allergen; avoid the trigger and use a "
                             "gentle moisturizer. See a doctor if it spreads or doesn't improve.",
        "guidance_text_de": "Meist durch einen Reizstoff oder ein Allergen verursacht; Auslöser meiden "
                             "und eine milde Feuchtigkeitscreme verwenden. Arzt aufsuchen, wenn es sich "
                             "ausbreitet oder nicht besser wird.",
        "source_dataset": "Disease-Symptom Knowledge Database",
    },
    {
        "condition_name": "Dental Caries",
        "icd_code": "K02",
        "category": "teeth",
        "associated_symptoms": ["tooth pain", "sensitivity"],
        "typical_severity": "URGENT",
        "guidance_text_en": "Tooth pain often indicates decay or infection. Book a dental appointment "
                             "soon to prevent it from worsening.",
        "guidance_text_de": "Zahnschmerzen deuten oft auf Karies oder eine Infektion hin. Vereinbaren "
                             "Sie bald einen Zahnarzttermin, um eine Verschlechterung zu vermeiden.",
        "source_dataset": "Disease-Symptom Knowledge Database",
    },
    {
        "condition_name": "Type 2 Diabetes (suspected)",
        "icd_code": "E11",
        "category": "diabetes",
        "associated_symptoms": ["excessive thirst", "frequent urination", "fatigue", "unexplained weight loss"],
        "typical_severity": "URGENT",
        "guidance_text_en": "This symptom pattern is worth discussing with a doctor for blood sugar "
                             "testing — early diagnosis makes management much easier.",
        "guidance_text_de": "Dieses Symptommuster sollte mit einem Arzt für einen Blutzuckertest "
                             "besprochen werden — eine frühe Diagnose erleichtert die Behandlung erheblich.",
        "source_dataset": "Disease-Symptom Knowledge Database",
    },
]

for row in KNOWLEDGE_BASE:
    exists = db.query(KnowledgeBase).filter_by(condition_name=row["condition_name"]).first()
    if not exists:
        db.add(KnowledgeBase(**row))

db.commit()
db.close()
print(f"Seeded {len(SYMPTOMS)} symptoms, {len(UI_CONTENT)} content keys, {len(KNOWLEDGE_BASE)} knowledge_base rows.")
print("NEXT: run `python -m scripts.embed_knowledge_base` to build the RAG vector store (Section 8.3).")
