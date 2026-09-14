"""
Clears all triage session data — meant to be run once, right before the
live demo, to wipe out test/debug sessions accumulated during development
(so the admin dashboard shows clean, real numbers when judges look at it).

This is destructive and irreversible. Run with:
    python -m scripts.clear_test_sessions

It will ask for a typed confirmation before deleting anything.
"""
from app.db.session import SessionLocal
from app.models.models import TriageSession, VisualAssessment

db = SessionLocal()

session_count = db.query(TriageSession).count()
visual_count = db.query(VisualAssessment).count()

print(f"This will permanently delete {session_count} triage session(s) and "
      f"{visual_count} visual assessment(s). This cannot be undone.")
confirm = input("Type DELETE to proceed: ")

if confirm != "DELETE":
    print("Aborted — no changes made.")
else:
    # Child records first — visual_assessments.session_id references
    # triage_sessions.id, and there's no ON DELETE CASCADE configured.
    db.query(VisualAssessment).delete()
    db.query(TriageSession).delete()
    db.commit()
    print(f"Deleted {session_count} session(s) and {visual_count} visual assessment(s).")

db.close()