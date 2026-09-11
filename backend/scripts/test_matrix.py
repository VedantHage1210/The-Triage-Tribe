"""
Cumulative verification test matrix for the Clinical Triage Assistant API.

Zero dependencies — uses only Python's standard library (urllib), so no
`pip install` is needed anywhere.

Still run this from YOUR OWN machine, NOT from the Railway console/shell:
  - The Railway container is serving live production traffic; the rate
    limit test in here deliberately fires 11 rapid requests, which has
    no business running inside the same process handling real users.
  - The whole point of this script is to hit the API as an outside,
    unauthenticated client would (real external IP, real network path).
    Running it from inside the container tests something different from
    what actually matters.

Usage:
    python test_matrix.py https://triage-tribe-api-production.up.railway.app

What it checks:
  1. /api/health is up
  2. Each category, in EN and DE, returns a real "llm" reading — not
     "fallback" (which would mean the LLM call failed)
  3. DE responses look like they're actually in German (crude heuristic;
     flags for manual review on FAIL, not a hard verdict)
  4. A red-flag phrase triggers the guardrail path (triggered_by ==
     "guardrail", severity == EMERGENCY) without touching the LLM
  5. A vague, low-confidence message triggers a follow-up round
  6. Hitting /api/triage 11 times fast from one IP gets a 429 on request 11
  7. The PDF report downloads (status 200, pdf content-type, real size)

Does NOT check mobile rendering — that still needs a manual look in
Chrome DevTools responsive mode.
"""
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

if len(sys.argv) != 2:
    print("Usage: python test_matrix.py <base_url>")
    sys.exit(1)

BASE = sys.argv[1].rstrip("/")
results = []


def check(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    results.append((name, status, detail))
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))


def http_get(path, params=None):
    url = f"{BASE}{path}"
    if params:
        query = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items())
        url = f"{url}?{query}"
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read(), dict(resp.getheaders())
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers)


def http_post_json(path, payload):
    url = f"{BASE}{path}"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method="POST", headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def post_triage(text, language="en", category=None, session_id=None):
    payload = {"text": text, "language": language, "category": category, "session_id": session_id}
    status, body = http_post_json("/api/triage", payload)
    try:
        parsed = json.loads(body) if body else {}
    except json.JSONDecodeError:
        parsed = {}
    return status, parsed

# 1. Health -------------------------------------------------------------
try:
    status, body, _ = http_get("/api/health")
    parsed = json.loads(body) if body else {}
    check("Health endpoint", status == 200 and parsed.get("status") == "ok", f"HTTP {status}: {body[:200]}")
except Exception as e:
    check("Health endpoint", False, str(e))

# 2. Categories in both languages ---------------------------------------
try:
    status, body, _ = http_get("/api/categories")
    cats = json.loads(body) if status == 200 else []
    category_codes = [c["code"] for c in cats] if cats else ["teeth", "eyes", "heart"]
except Exception:
    category_codes = ["teeth", "eyes", "heart"]

SAMPLE_TEXT = {
    "en": "I have had a dull ache here for two days, it gets a bit worse in the evening.",
    "de": "Ich habe seit zwei Tagen einen dumpfen Schmerz hier, abends wird es etwas schlimmer.",
}
GERMAN_MARKERS = ["der", "die", "das", "und", "sie", "ist", "nicht", "für", "ärztlich", "beschwerden"]

for cat in category_codes:
    for lang in ("en", "de"):
        try:
            status, body = post_triage(SAMPLE_TEXT[lang], language=lang, category=cat)
            is_llm = body.get("triggered_by") == "llm"
            has_content = bool(body.get("reasoning")) and bool(body.get("recommended_action"))
            check(
                f"{cat} / {lang}: real LLM reading (not fallback)",
                status == 200 and is_llm and has_content,
                f"HTTP {status}, triggered_by={body.get('triggered_by')}",
            )
            if lang == "de" and is_llm:
                text_blob = (body.get("reasoning", "") + " " + body.get("recommended_action", "")).lower()
                looks_german = any(w in text_blob for w in GERMAN_MARKERS)
                check(
                    f"{cat} / de: reasoning looks German (heuristic, check manually if FAIL)",
                    looks_german,
                    text_blob[:120],
                )
        except Exception as e:
            check(f"{cat} / {lang}: request", False, str(e))
        time.sleep(1)  # stay under the 10/minute limit while testing

# 3. Emergency guardrail --------------------------------------------------
try:
    status, body = post_triage("I have crushing chest pain and can't breathe", language="en")
    check(
        "Emergency guardrail fires without hitting the LLM",
        status == 200 and body.get("triggered_by") == "guardrail" and body.get("severity") == "EMERGENCY",
        f"triggered_by={body.get('triggered_by')}, severity={body.get('severity')}",
    )
    emergency_session_id = body.get("session_id")
    emergency_token = body.get("report_token")
except Exception as e:
    check("Emergency guardrail", False, str(e))
    emergency_session_id = emergency_token = None

time.sleep(2)

# 4. Follow-up round --------------------------------------------------
try:
    status, body = post_triage("something feels a bit off", language="en")
    check(
        "Vague input triggers a follow-up round",
        status == 200 and body.get("needs_follow_up") is True and len(body.get("follow_up_questions") or []) > 0,
        f"needs_follow_up={body.get('needs_follow_up')}, questions={body.get('follow_up_questions')}",
    )
except Exception as e:
    check("Follow-up round", False, str(e))

# 5. PDF download ----------------------------------------------------------
if emergency_session_id and emergency_token:
    for lang in ("en", "de"):
        try:
            status, body, headers = http_get(
                f"/api/triage/{emergency_session_id}/report.pdf",
                params={"lang": lang, "token": emergency_token},
            )
            content_type = headers.get("Content-Type", "") or headers.get("content-type", "")
            ok = status == 200 and content_type.startswith("application/pdf") and len(body) > 1000
            check(f"PDF report downloads ({lang})", ok, f"HTTP {status}, {len(body)} bytes")
        except Exception as e:
            check(f"PDF report downloads ({lang})", False, str(e))
else:
    check("PDF report downloads", False, "skipped — no session/token from guardrail step")

# 6. Rate limit (run LAST — deliberately trips the limiter) ----------------
print("\nFiring 11 rapid requests to confirm the 10/minute rate limit...")
codes = []
for i in range(11):
    try:
        status, _ = post_triage("quick rate limit probe message", language="en")
        codes.append(status)
    except Exception as e:
        codes.append(f"error:{e}")
check(
    "Rate limit returns 429 on the 11th request",
    codes[-1] == 429,
    f"status codes: {codes}",
)

# Summary -------------------------------------------------------------
print("\n" + "=" * 60)
passed = sum(1 for _, s, _ in results if s == "PASS")
print(f"{passed}/{len(results)} checks passed")
for name, status, detail in results:
    if status == "FAIL":
        print(f"  FAILED: {name} ({detail})")
print("=" * 60)
print("NOT covered by this script — check manually:")
print("  - Mobile rendering (Chrome DevTools responsive mode, 375px width)")
print("  - Visual correctness of the PDF layout (open the downloaded file)")
