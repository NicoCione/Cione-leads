# Cione Leads

Lead-generation + outreach-tracking pipeline for Cione Solutions.
Targets small home remodeling / restoration / construction companies,
audits their websites for automation gaps, and tracks outreach in a
mobile-friendly dashboard backed by Supabase.

## Pipeline

1. **`places_fetch.py`** — pulls business leads from Google Places
2. **`website_audit.py`** — audits each site for automation-gap signals
   (no online booking, no live chat, no CRM, DIY platform, etc.) and
   generates a "why reach out" opener line
3. **`apollo_enrich.py`** — (optional) finds owner/manager contact via Apollo
4. **`supabase_push.py`** — pushes leads into Supabase
5. **`run.py`** — runs the whole thing

## Dashboard

`dashboard-supabase.html` — login, filter, sort by signal strength, track
status (New → Contacted → Replied → Meeting → Won/Dead), add notes, copy
openers, tap-to-call. Syncs across devices via Supabase realtime.

## Setup

See **`DEPLOY.md`** for full step-by-step. Short version:

1. `cp config.example.py config.py` and fill in your keys
2. Run `schema.sql` in your Supabase SQL editor
3. `pip install -r requirements.txt`
4. `python run.py`
5. Host the dashboard (Cloudflare Pages / Vercel)

## License

MIT — see `LICENSE`.

## Security

- `config.py` holds secrets and is **gitignored** — never commit it.
  Use `config.example.py` as the template.
- `index.html` (hosting build with embedded anon key) is gitignored too.
  The committed `dashboard-supabase.html` prompts for credentials at runtime.
- Never commit your `service_role` key anywhere.

## Files

| File | Purpose |
|------|---------|
| `run.py` | Main pipeline runner |
| `places_fetch.py` | Google Places lead fetcher |
| `website_audit.py` | Website signal auditor |
| `apollo_enrich.py` | Optional contact enrichment |
| `supabase_push.py` | Pushes leads to Supabase |
| `schema.sql` | Database schema |
| `dashboard-supabase.html` | The dashboard (keyless, commit-safe) |
| `config.example.py` | Config template |
| `DEPLOY.md` | Full deploy guide |
