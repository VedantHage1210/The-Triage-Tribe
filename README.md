# AI-Powered Clinical Triage Assistant

Working scaffold built against the full roadmap. Implements Day 1-9 core:
guardrail safety layer, RAG-grounded AI pipeline with adaptive follow-up,
bilingual (EN/DE) patient app, PDF reports, scoped image observation
(eyes/skin), and a full admin panel.

## What's implemented
- ✅ Full DB schema — all 7 tables (Section 5, 8.5, 10.3, 11.2).
- ✅ Deterministic guardrail layer (instant EMERGENCY, EN + DE keywords).
- ✅ Full AI pipeline: extraction → RAG retrieval → grounded classification
  with confidence → adaptive multi-turn follow-up (max 2 rounds).
- ✅ Category system (8 categories), category-filtered RAG retrieval.
- ✅ Bilingual UI content served from DB, EN default.
- ✅ Patient app: category grid → triage flow → result card with cited
  conditions → optional photo upload (eyes/skin) → non-diagnostic AI
  observation → PDF report download.
- ✅ PDF report generation (WeasyPrint, bilingual, doctor-visit style).
- ✅ Image-based visual observation — scoped to eyes/skin only, qualitative
  language only, never a percentage or diagnosis (Section 10.1 hard rule).
- ✅ Admin panel: JWT login, symptom CRUD (bilingual fields), UI content
  editor (bilingual, one save = both languages), knowledge base CRUD,
  session log with signed PDF links.
- ✅ Security hardening: signed short-lived report access, production config
  validation, security headers, stronger bilingual red-flag matching, and
  explicit urgent fallback when the AI service is unavailable.
- ✅ Seed script + embedding script + first-admin-user script.

## What's NOT yet built
- ⬜ Knowledge-base admin form and automatic re-embedding after edits. The
  protected CRUD API is available; vector embeddings still need to be rebuilt
  after content changes.
- ⬜ Teeth/other-category image support — intentionally out of scope for
  v1 (Section 1.4).

## Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # fill in DATABASE_URL and LLM_API_KEY
# Make sure Postgres is running and the DB exists, e.g.: createdb triage_db
alembic upgrade head

uvicorn app.main:app --reload --port 8000
```

In a second terminal:
```bash
cd backend && source venv/bin/activate
python -m scripts.seed_data
python -m scripts.embed_knowledge_base
python -m scripts.create_admin admin@example.com yourpassword
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env             # defaults point at localhost:8000
npm run dev
```
- Patient app: http://localhost:5173
- Admin panel: http://localhost:5173/admin/login (use the email/password
  from `create_admin` above)

## Quick smoke test
1. Pick "Heart / Cardiac" → type "I have chest pain and can't breathe" →
   instant **EMERGENCY** (guardrail, no LLM call).
2. Pick "Eyes" → type "my eye has been red and itchy for two days" → full
   AI pipeline, should cite "Conjunctivitis". Upload a photo → get a
   qualitative, non-diagnostic observation. Download the PDF report.
3. Switch to DE and repeat — UI and AI response come back in German.
4. Log into `/admin/login` → edit a symptom's EN/DE label → refresh the
   patient app's category screen to confirm it reflects instantly.

## Folder structure & full spec
See `Clinical_Triage_Assistant_Roadmap.md` for the complete architecture,
RAG design, and day-wise plan this scaffold follows.
