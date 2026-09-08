"""
Deterministic guardrail layer — Section 7.1.
Runs BEFORE any LLM call. If a red-flag symptom keyword matches (in either
English or German), we return EMERGENCY instantly, without waiting on the
LLM. This is the fastest and most reliable safety net in the whole system.

IMPORTANT (Section 15/19 in the roadmap): keep this list reviewed for both
languages — German medical terms differ from a literal translation
(e.g. "Brustschmerzen" for chest pain, not a word-for-word translation).
"""
import re

from sqlalchemy.orm import Session

from app.models.models import Symptom

# Fallback in-memory list used only if the DB has no red-flag symptoms seeded
# yet — keeps the guardrail functional from day one, before Day 2 seeding.
DEFAULT_RED_FLAG_TERMS = {
    "en": [
        "chest pain", "can't breathe", "cannot breathe", "difficulty breathing",
        "unconscious", "unresponsive", "severe bleeding", "heavy bleeding",
        "stroke", "face drooping", "slurred speech", "suicidal", "seizure",
        "severe allergic reaction", "anaphylaxis", "not breathing", "blue lips",
        "vomiting blood", "blood in vomit", "sudden severe headache",
    ],
    "de": [
        "brustschmerzen", "kann nicht atmen", "atemnot", "bewusstlos",
        "starke blutung", "schlaganfall", "hängendes gesicht",
        "undeutliche sprache", "selbstmordgedanken", "krampfanfall",
        "schwere allergische reaktion", "anaphylaxie", "atmet nicht", "blaue lippen",
        "bluterbrechen", "blut im erbrochenen", "plötzlicher starker kopfschmerz",
    ],
}


def contains_red_flag_terms(text: str, terms: list[str]) -> bool:
    normalized_text = re.sub(r"[^\w\s]", " ", text.casefold())
    normalized_text = re.sub(r"\s+", " ", normalized_text).strip()
    return any(
        re.search(rf"\b{re.escape(term.casefold())}\b", normalized_text)
        for term in terms
    )


def check_red_flags(text: str, language: str, db: Session) -> bool:
    """
    Returns True if the input text matches a known red-flag symptom.
    Checks the DB-managed symptom list first (admin-editable), falls back
    to the hardcoded list above if the DB has nothing seeded yet.
    """
    db_red_flags = (
        db.query(Symptom)
        .filter(Symptom.red_flag == True)  # noqa: E712
        .all()
    )

    if db_red_flags:
        for symptom in db_red_flags:
            label = symptom.label_de if language == "de" and symptom.label_de else symptom.label_en
            if label and contains_red_flag_terms(text, [label]):
                return True
        return False

    # DB not seeded yet — use the hardcoded fallback list
    terms = DEFAULT_RED_FLAG_TERMS.get(language, DEFAULT_RED_FLAG_TERMS["en"])
    return contains_red_flag_terms(text, terms)
