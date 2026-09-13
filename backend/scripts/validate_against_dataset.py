"""
Validates the deterministic safety guardrail against the synthetic,
de-identified triage dataset provided at the MunichTech EXPO briefing
(data/clinical-triage-sample-2026.csv, 400 records, ESI-labeled).

This checks ONLY the guardrail layer (symptom red-flag terms + vital-sign
thresholds) — the layer that runs before any LLM call. It does not call
the LLM, so it costs nothing to run and has no external dependencies
beyond the standard library plus this project's own guardrail module.

Run with:
    python -m scripts.validate_against_dataset

What "correct" means here: ESI-1 (Immediate) and ESI-2 (Emergent) are the
two most urgent of the five ESI levels — a real ED would want these
flagged as an emergency. ESI-3/4/5 should NOT be flagged as an emergency
by the guardrail alone (they still get a full assessment — just not the
instant, no-LLM emergency shortcut).
"""
import csv
from pathlib import Path

from app.services.guardrail import DEFAULT_RED_FLAG_TERMS, check_vital_red_flags, contains_red_flag_terms

DATASET_PATH = Path(__file__).resolve().parent.parent / "data" / "clinical-triage-sample-2026.csv"


class _Vitals:
    """Mimics the VitalSigns schema's attribute shape for this offline check."""
    def __init__(self, hr, bp_sys, spo2, temp):
        self.heart_rate_bpm = hr
        self.bp_systolic = bp_sys
        self.bp_diastolic = None
        self.temperature_c = temp
        self.spo2_percent = spo2


def main():
    with open(DATASET_PATH) as f:
        rows = list(csv.DictReader(f))

    by_esi = {i: [0, 0] for i in range(1, 6)}  # esi -> [caught, total]

    for r in rows:
        esi = int(r["esi_level"])
        vitals = _Vitals(
            hr=float(r["heart_rate"]),
            bp_sys=float(r["systolic_bp"]),
            spo2=float(r["spo2"]),
            temp=float(r["temperature_c"]),
        )
        vitals_flag, _ = check_vital_red_flags(vitals, "en")
        symptom_flag = contains_red_flag_terms(r["chief_complaint"], DEFAULT_RED_FLAG_TERMS["en"])
        caught = vitals_flag or symptom_flag

        by_esi[esi][1] += 1
        if caught:
            by_esi[esi][0] += 1

    print(f"Validated against {len(rows)} records from {DATASET_PATH.name}\n")
    print(f"{'ESI level':<28}{'Caught':<10}{'Total':<8}{'Rate'}")
    labels = {1: "ESI-1 Immediate", 2: "ESI-2 Emergent", 3: "ESI-3 Urgent", 4: "ESI-4 Less Urgent", 5: "ESI-5 Non-Urgent"}
    for esi in range(1, 6):
        c, t = by_esi[esi]
        print(f"{labels[esi]:<28}{c:<10}{t:<8}{c/t*100:.1f}%")

    true_emergency_caught = by_esi[1][0] + by_esi[2][0]
    true_emergency_total = by_esi[1][1] + by_esi[2][1]
    false_positives = by_esi[4][0] + by_esi[5][0]
    false_positive_total = by_esi[4][1] + by_esi[5][1]

    print(f"\nESI-1+2 (true emergencies) caught by the guardrail alone — no LLM call:")
    print(f"  {true_emergency_caught}/{true_emergency_total} = {true_emergency_caught/true_emergency_total*100:.1f}% recall")
    print(f"False positives on ESI-4/5 (non-urgent flagged as emergency):")
    print(f"  {false_positives}/{false_positive_total}")


if __name__ == "__main__":
    main()