from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["categories"])

# Section 9.1 — v1 categories. image_support flags which ones show the
# optional photo-upload step (Section 10, scoped to eyes + skin only).
CATEGORIES = [
    {"code": "eyes", "label_en": "Eyes", "label_de": "Augen", "image_support": True},
    {"code": "skin", "label_en": "Skin", "label_de": "Haut", "image_support": True},
    {"code": "teeth", "label_en": "Teeth / Dental", "label_de": "Zähne", "image_support": False},
    {"code": "heart", "label_en": "Heart / Cardiac", "label_de": "Herz", "image_support": False},
    {"code": "digestion", "label_en": "Digestion", "label_de": "Verdauung", "image_support": False},
    {"code": "diabetes", "label_en": "Diabetes / Metabolic", "label_de": "Diabetes", "image_support": False},
    {"code": "weight", "label_en": "Weight / Nutrition", "label_de": "Gewicht", "image_support": False},
    {"code": "general", "label_en": "General / Other", "label_de": "Allgemein", "image_support": False},
]


@router.get("/categories")
def list_categories():
    return CATEGORIES
