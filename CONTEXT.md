# Project Context — Cione Leads

Handoff notes for picking up work on this project in a fresh session.

## What this is

A lead-generation + outreach-tracking pipeline for Cione Solutions, targeting
small home remodeling / restoration / construction companies (~5–50 employees)
that lack CRM and automation infrastructure.

**Pipeline:** Google Places (find businesses) → website audit (detect automation
gaps and generate a "why reach out" opener) → optional Apollo enrichment (find
owner/manager contact) → push to Supabase. Results also written to CSV.

**Dashboard:** mobile-first HTML app for working the list — login, filter, sort
by signal strength, track status (New → Contacted → Replied → Meeting → Won/Dead),
add notes, copy openers, tap-to-call. Backed by Supabase with realtime sync.

## Current state

### Done
- All pipeline code written: `places_fetch.py`, `website_audit.py`,
  `apollo_enrich.py`, `supabase_push.py`, `run.py`.
- Two dashboards: `dashboard-supabase.html` (keyless, commit-safe, prompts for
  creds at runtime) and `index.html` (same app with project URL + anon key
  hardcoded for hosting).
- Browser-only fallback dashboard: `dashboard.html` (no backend, uses local storage).
- Supabase project `cione-leads` created and LIVE:
  - project ref: `bwoexsdalrrkhkkcrmht`
  - region: us-east-1
  - The `leads` table, indexes, RLS policies, and realtime publication are
    ALREADY APPLIED (see `schema.sql`). Do not re-run unless rebuilding.

### Repo cleanup needed (priority)
1. **Remove `config.py` from the repo** — it was committed by accident. It holds
   the live Supabase project URL. Should be gitignored, never committed.
2. **Decide on `index.html`** — it has the anon key embedded. Anon keys are
   public-safe (RLS protects data), so it's fine in a PRIVATE repo. If the repo
   is PUBLIC, remove `index.html` from the repo and keep it local for hosting;
   the committed dashboard should be the keyless `dashboard-supabase.html`.
3. **Add `.gitignore`** — it's missing (the GitHub web drag-drop uploader skipped
   the dotfile). Needed so `config.py` / `index.html` / CSV stay out. Contents:
   ```
   config.py
   *.env
   .env
   index.html
   cione_leads.csv
   cione_leads_progress.csv
   __pycache__/
   *.pyc
   .venv/
   venv/
   .DS_Store
   ```

### Still to do to go live
- **Rotate the Supabase service_role key** — it was exposed in chat. Supabase →
  Project Settings → API → reset service_role key. Put the new one ONLY in local
  `config.py`, never commit it.
- **Fill in local `config.py`** (copy from `config.example.py`):
  - `GOOGLE_PLACES_API_KEY` (Google Cloud Console, enable "Places API (New)")
  - `SUPABASE_SERVICE_KEY` (the rotated one)
  - `SUPABASE_OWNER_ID` (see next step)
  - `SUPABASE_URL` is already `https://bwoexsdalrrkhkkcrmht.supabase.co`
  - optionally `APOLLO_API_KEY`
  - set `SEARCH_QUERIES` and `TARGET_LOCATIONS` (currently PA cities)
- **Create login + get owner ID:** open the dashboard, sign up with email/password,
  then Supabase → Authentication → Users → copy your UID into `SUPABASE_OWNER_ID`.
  (Consider turning off email confirmation in Auth settings for instant login.)
- **Run:** `pip install -r requirements.txt` then `python run.py`.
- **Host:** rename `dashboard-supabase.html` (or use `index.html`) and deploy to
  Cloudflare Pages or Vercel. Add to phone home screen. See `DEPLOY.md`.

## Key facts / gotchas
- Google Places Text Search caps at 60 results per query — the code tiles across
  query × location combos to widen coverage.
- `supabase_push.py` uses the service_role key (server-side, bypasses RLS). The
  dashboard uses the anon key (browser, RLS-enforced). Never swap these.
- Upserts are keyed on `(owner_id, dedupe_key)` where dedupe_key = name|address,
  so re-running `run.py` updates rows instead of duplicating, preserving status/notes.
- `website_audit.py` reads raw HTML, so JS-heavy sites can throw false "missing
  tool" flags. Fine for small-business targets; spot-check top results before sending.

## Files
| File | Purpose |
|------|---------|
| `run.py` | Main pipeline runner |
| `places_fetch.py` | Google Places lead fetcher |
| `website_audit.py` | Website signal auditor + opener generator |
| `apollo_enrich.py` | Optional owner/email enrichment |
| `supabase_push.py` | Pushes leads to Supabase (service_role) |
| `schema.sql` | DB schema (already applied to the project) |
| `dashboard-supabase.html` | Dashboard, keyless / commit-safe |
| `index.html` | Dashboard with URL+anon key hardcoded (local/hosting only) |
| `dashboard.html` | Browser-only fallback, no backend |
| `config.example.py` | Config template (commit this) |
| `config.py` | Real config with secrets (DO NOT commit) |
| `requirements.txt` | Python deps |
| `DEPLOY.md` | Full deploy walkthrough |
| `README.md` | Project overview |
