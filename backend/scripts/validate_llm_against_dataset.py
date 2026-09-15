"""
Validates the FULL triage pipeline (guardrail, then RAG-grounded LLM
classification for anything the guardrail doesn't catch) against the
synthetic ESI-labeled dataset from the challenge briefing.

Unlike validate_against_dataset.py (guardrail only, free, instant), this
script calls the real Gemini API for every record the guardrail doesn't
resolve deterministically — it costs real quota and takes real time.

ESI -> our severity mapping used for comparison:
    ESI-1 Immediate, ESI-2 Emergent  -> EMERGENCY
    ESI-3 Urgent                     -> URGENT
    ESI-4 Less Urgent                -> ROUTINE
    ESI-5 Non-Urgent                 -> SELF_CARE

Run with (from backend/):
    python -m scripts.validate_llm_against_dataset --limit 40
    python -m scripts.validate_llm_against_dataset --all      # all 400, slow

Requires real LLM_PROVIDER / LLM_API_KEY / LLM_MODEL env vars to be set,
same as production. Adds a delay between LLM-calling records to stay
within Gemini's rate limits — adjust --delay if you hit 429s.
"""
import argparse
import csv
import time
from pathlib import Path

from app.services.guardrail import DEFAULT_RED_FLAG_TERMS, check_vital_red_flags, contains_red_flag_terms
from app.services.triage_orchestrator import run_triage_pipeline
from app.services.errors import TriagePipelineError

DATASET_PATH = Path(__file__).resolve().parent.parent / "data" / "clinical-triage-sample-2026.csv"

ESI_TO_TARGET = {1: "EMERGENCY", 2: "EMERGENCY", 3: "URGENT", 4: "ROUTINE", 5: "SELF_CARE"}
SEVERITY_RANK = {"EMERGENCY": 0, "URGENT": 1, "ROUTINE": 2, "SELF_CARE": 3}


class _Vitals:
    def __init__(self, hr, bp_sys, spo2, temp):
        self.heart_rate_bpm = hr
        self.bp_systolic = bp_sys
        self.bp_diastolic = None
        self.temperature_c = temp
        self.spo2_percent = spo2


def guardrail_fires(row) -> bool:
    vitals = _Vitals(
        hr=float(row["heart_rate"]), bp_sys=float(row["systolic_bp"]),
        spo2=float(row["spo2"]), temp=float(row["temperature_c"]),
    )
    vitals_flag, _ = check_vital_red_flags(vitals, "en")
    symptom_flag = contains_red_flag_terms(row["chief_complaint"], DEFAULT_RED_FLAG_TERMS["en"])
    return vitals_flag or symptom_flag


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=40, help="Max non-guardrail (LLM-calling) records to test. Ignored with --all.")
    parser.add_argument("--all", action="store_true", help="Run all records the guardrail doesn't catch (309 by default data) — slow, uses real quota.")
    parser.add_argument("--delay", type=float, default=3.0, help="Seconds to sleep between LLM-calling records (rate-limit safety).")
    args = parser.parse_args()

    with open(DATASET_PATH) as f:
        rows = list(csv.DictReader(f))

    # Evenly sample across ESI 3/4/5 (the records the guardrail correctly
    # does NOT flag) so a --limit run still covers all three severities,
    # rather than exhausting the quota on the first N rows of the file.
    by_esi345 = {3: [], 4: [], 5: []}
    guardrail_rows = []
    for r in rows:
        esi = int(r["esi_level"])
        if guardrail_fires(r):
            guardrail_rows.append(r)
        else:
            by_esi345[esi].append(r)

    llm_rows = []
    if args.all:
        for esi in (3, 4, 5):
            llm_rows.extend(by_esi345[esi])
    else:
        per_bucket = max(1, args.limit // 3)
        for esi in (3, 4, 5):
            llm_rows.extend(by_esi345[esi][:per_bucket])

    print(f"Guardrail resolves {len(guardrail_rows)}/{len(rows)} records instantly (no LLM call).")
    print(f"Testing the LLM path on {len(llm_rows)} record(s) not caught by the guardrail "
          f"({'all remaining' if args.all else f'sampled, limit={args.limit}'}).\n")

    results = []  # (esi, target, predicted, source, ok)

    for r in guardrail_rows:
        esi = int(r["esi_level"])
        results.append((esi, "EMERGENCY", "EMERGENCY", "guardrail", True))

    errors = 0
    for i, r in enumerate(llm_rows):
        esi = int(r["esi_level"])
        target = ESI_TO_TARGET[esi]
        vitals = _Vitals(
            hr=float(r["heart_rate"]), bp_sys=float(r["systolic_bp"]),
            spo2=float(r["spo2"]), temp=float(r["temperature_c"]),
        )
        try:
            result, _, _ = run_triage_pipeline(
                text=r["chief_complaint"], language="en", category=None, db=None, vitals=vitals,
            )
            predicted = result.severity.value if hasattr(result.severity, "value") else result.severity
            results.append((esi, target, predicted, "llm", predicted == target))
            print(f"[{i+1}/{len(llm_rows)}] ESI-{esi} '{r['chief_complaint']}' -> predicted {predicted} (target {target})")
        except (TriagePipelineError, Exception) as e:
            errors += 1
            print(f"[{i+1}/{len(llm_rows)}] ESI-{esi} '{r['chief_complaint']}' -> ERROR: {e}")
        time.sleep(args.delay)

    # ---- Summary ----
    print("\n" + "=" * 70)
    total = len(results)
    exact_matches = sum(1 for _, t, p, _, _ in results if t == p)
    under_triage = sum(1 for _, t, p, _, _ in results if SEVERITY_RANK.get(p, 9) > SEVERITY_RANK.get(t, -1))
    over_triage = sum(1 for _, t, p, _, _ in results if SEVERITY_RANK.get(p, 9) < SEVERITY_RANK.get(t, -1))

    print(f"Total classified: {total} (+{errors} error(s), not counted above)")
    print(f"Exact match with ESI-derived target: {exact_matches}/{total} = {exact_matches/total*100:.1f}%")
    print(f"Under-triaged (predicted LESS urgent than target — the dangerous direction): {under_triage}")
    print(f"Over-triaged (predicted MORE urgent than target — safer direction): {over_triage}")

    print("\nBy source:")
    for source in ("guardrail", "llm"):
        sub = [x for x in results if x[3] == source]
        if not sub:
            continue
        ok = sum(1 for x in sub if x[4])
        print(f"  {source}: {ok}/{len(sub)} = {ok/len(sub)*100:.1f}%")

    print("\nBy ESI level (LLM-path records only):")
    for esi in (3, 4, 5):
        sub = [x for x in results if x[0] == esi and x[3] == "llm"]
        if not sub:
            continue
        ok = sum(1 for x in sub if x[4])
        print(f"  ESI-{esi}: {ok}/{len(sub)} = {ok/len(sub)*100:.1f}%")


if __name__ == "__main__":
    main()