"""
Shared rate-limiter instance. /api/triage is public and unauthenticated —
every call spends real LLM quota/billing. Without a limit, a single
script can exhaust the Gemini quota (or run up a bill) in minutes.
Keyed by IP; fine for a single-instance deploy like this one.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
