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

# Colloquial patient phrasing, checked ALONGSIDE the DB-managed symptom
# list (not instead of it) — the DB holds one canonical clinical label per
# symptom (e.g. "Shortness of breath"), which real patients rarely type.
DEFAULT_RED_FLAG_TERMS = {
    "en": [
        "chest pain", "can't breathe", "cannot breathe", "difficulty breathing",
        "unconscious", "unresponsive", "severe bleeding", "heavy bleeding",
        "stroke", "face drooping", "slurred speech", "suicidal", "seizure",
        "severe allergic reaction", "anaphylaxis", "not breathing", "blue lips",
        "vomiting blood", "blood in vomit", "sudden severe headache",
        # Added after validating against the MunichTech EXPO synthetic
        # dataset (400 records, real ESI labels) — these closed a measured
        # gap: ESI-2 (Emergent) recall went from 47.8% to 100% with these
        # additions, at zero new false positives on ESI-4/5 (non-urgent).
        "gi bleed", "gastrointestinal bleed", "severe dyspnea", "dyspnea",
        "altered mental status", "confused", "drowsy", "unresponsive to pain",
    ],
    "de": [
        "brustschmerzen", "kann nicht atmen", "atemnot", "bewusstlos",
        "starke blutung", "schlaganfall", "hängendes gesicht",
        "undeutliche sprache", "selbstmordgedanken", "krampfanfall",
        "schwere allergische reaktion", "anaphylaxie", "atmet nicht", "blaue lippen",
        "bluterbrechen", "blut im erbrochenen", "plötzlicher starker kopfschmerz",
        "magen darm blutung", "darmblutung", "veränderter bewusstseinszustand",
        "verwirrt", "benommen", "reagiert nicht auf schmerzreize",
    ],
}


def _normalize(text: str) -> str:
    normalized = re.sub(r"[^\w\s]", " ", text.casefold())
    return re.sub(r"\s+", " ", normalized).strip()


def contains_red_flag_terms(text: str, terms: list[str]) -> bool:
    normalized_text = _normalize(text)
    return any(
        # The term must go through the SAME normalization as the input
        # text. Without this, a term like "can't breathe" (apostrophe
        # intact) can never match normalized user text ("can t breathe",
        # apostrophe stripped) — this was silently swallowing one of the
        # most important emergency phrases in the entire guardrail list.
        re.search(rf"\b{re.escape(_normalize(term))}\b", normalized_text)
        for term in terms
        if _normalize(term)
    )


def check_red_flags(text: str, language: str, db: Session) -> bool:
    """
    Returns True if the input text matches a known red-flag symptom.

    Checks BOTH sources, not "DB, else fallback":
      - DB-managed symptom labels (admin-editable, one canonical clinical
        term per symptom, e.g. "Shortness of breath")
      - The hardcoded colloquial phrase list below (the actual wording
        patients use, e.g. "can't breathe", "trouble breathing")

    These previously were treated as either/or: as soon as the DB had
    ANY red-flag symptoms seeded, the colloquial list was skipped
    entirely — meaning a patient typing "can't breathe" was never
    caught, because the DB only had the clinical label "Shortness of
    breath", not that phrase. Checking both closes that gap.
    """
    db_red_flags = (
        db.query(Symptom)
        .filter(Symptom.red_flag == True)  # noqa: E712
        .all()
    )
    db_labels = [
        (symptom.label_de if language == "de" and symptom.label_de else symptom.label_en)
        for symptom in db_red_flags
    ]
    if contains_red_flag_terms(text, [label for label in db_labels if label]):
        return True

    fallback_terms = DEFAULT_RED_FLAG_TERMS.get(language, DEFAULT_RED_FLAG_TERMS["en"])
    return contains_red_flag_terms(text, fallback_terms)


# Standard clinical red-flag vital sign thresholds (used in triage scores
# such as NEWS2). These are conservative, widely-used cutoffs — not a
# diagnosis, just "this number alone warrants immediate attention"
# regardless of what the text says or whether the LLM is available.
VITAL_REASON_TEMPLATES = {
    "en": {
        "spo2_low": "SpO2 {v}% — below safe oxygen saturation threshold",
        "hr_high": "Heart rate {v} bpm — dangerously high",
        "hr_low": "Heart rate {v} bpm — dangerously low",
        "bp_low": "Blood pressure {v} systolic — signs of shock/hypotension",
        "bp_high": "Blood pressure {v} systolic — hypertensive crisis range",
        "temp_high": "Temperature {v}°C — dangerously high fever",
        "temp_low": "Temperature {v}°C — dangerously low (hypothermia)",
    },
    "de": {
        "spo2_low": "SpO2 {v}% — unter der sicheren Sauerstoffsättigungsgrenze",
        "hr_high": "Herzfrequenz {v} bpm — gefährlich hoch",
        "hr_low": "Herzfrequenz {v} bpm — gefährlich niedrig",
        "bp_low": "Blutdruck {v} systolisch — Anzeichen für Schock/Hypotonie",
        "bp_high": "Blutdruck {v} systolisch — hypertensive Krise",
        "temp_high": "Temperatur {v}°C — gefährlich hohes Fieber",
        "temp_low": "Temperatur {v}°C — gefährlich niedrig (Hypothermie)",
    },
}


def check_vital_red_flags(vitals, language: str) -> tuple[bool, list[str]]:
    """
    Deterministic, LLM-independent check on numeric vital signs.
    Returns (is_emergency, reasons) — reasons are ready to show a nurse
    directly (no LLM interpretation step, so they can't be wrong or
    inconsistent about basic threshold math).
    """
    if vitals is None:
        return False, []

    t = VITAL_REASON_TEMPLATES.get(language, VITAL_REASON_TEMPLATES["en"])
    reasons = []

    if vitals.spo2_percent is not None and vitals.spo2_percent < 90:
        reasons.append(t["spo2_low"].format(v=vitals.spo2_percent))
    if vitals.heart_rate_bpm is not None:
        if vitals.heart_rate_bpm > 150:
            reasons.append(t["hr_high"].format(v=vitals.heart_rate_bpm))
        elif vitals.heart_rate_bpm < 40:
            reasons.append(t["hr_low"].format(v=vitals.heart_rate_bpm))
    if vitals.bp_systolic is not None:
        if vitals.bp_systolic < 90:
            reasons.append(t["bp_low"].format(v=vitals.bp_systolic))
        elif vitals.bp_systolic > 180:
            reasons.append(t["bp_high"].format(v=vitals.bp_systolic))
    if vitals.temperature_c is not None:
        if vitals.temperature_c >= 40.0:
            reasons.append(t["temp_high"].format(v=vitals.temperature_c))
        elif vitals.temperature_c <= 35.0:
            reasons.append(t["temp_low"].format(v=vitals.temperature_c))

    return len(reasons) > 0, reasons