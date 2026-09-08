import logging
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.models import TriageSession, VisualAssessment
from app.schemas.triage_schema import VisualCheckResult
from app.services.vision_service import analyze_image

router = APIRouter(prefix="/api", tags=["visual-check"])
logger = logging.getLogger(__name__)

ALLOWED_CATEGORIES = {"eyes", "skin"}  # Section 10.1 — hard scope limit for v1
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE_BYTES = 8 * 1024 * 1024  # 8MB

FALLBACK_NOTE = {
    "en": "We couldn't analyze this image right now. Please consult a professional "
          "for an in-person assessment.",
    "de": "Wir konnten dieses Bild gerade nicht analysieren. Bitte konsultieren Sie "
          "einen Facharzt für eine persönliche Untersuchung.",
}


@router.post("/visual-check", response_model=VisualCheckResult)
async def visual_check(
    session_id: UUID = Form(...),
    category: str = Form(...),
    language: str = Form("en"),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if category not in ALLOWED_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Visual observation is only available for: {', '.join(ALLOWED_CATEGORIES)}",
        )

    session = db.get(TriageSession, session_id)
    if not session or session.category != category:
        raise HTTPException(status_code=404, detail="Triage session not found")
    if language not in {"en", "de"}:
        raise HTTPException(status_code=400, detail="Unsupported language")

    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported image type. Use JPEG, PNG, or WEBP.")

    image_bytes = await image.read()
    if len(image_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="Image too large (max 8MB).")

    try:
        result = analyze_image(image_bytes, image.content_type, category, language)
    except Exception:
        logger.exception("Visual observation failed; returning safe fallback.")
        result = VisualCheckResult(
            visible_features=[],
            general_note=FALLBACK_NOTE.get(language, FALLBACK_NOTE["en"]),
            recommend_professional_check=True,
            image_quality_sufficient=False,
        )

    # Section 10.3 — persist only the text observation, never the raw image
    # (privacy hygiene, mentioned explicitly in the roadmap's pitch notes).
    assessment = VisualAssessment(
        session_id=session_id,
        category=category,
        visible_features=result.visible_features,
        general_note=result.general_note,
        image_quality_sufficient=result.image_quality_sufficient,
    )
    db.add(assessment)
    db.commit()

    return result
