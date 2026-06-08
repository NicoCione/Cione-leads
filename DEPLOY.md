# Cione Leads — Deploy Guide (Option B: Supabase + hosted dashboard)

Everything's built. Here's the click-by-click for when you're back at your laptop.
Whole thing takes ~20–30 min.

---

## Part 1 — Supabase (the database)

1. **Create a project** at https://supabase.com/dashboard
   - I'd name it `cione-leads` to keep it separate from BeeToBee and your other project.
   - Pick the US East region (matches your existing setup). Save the DB password somewhere.

2. **Run the schema**
   - Open the project → **SQL Editor** → New query
   - Paste the entire contents of `schema.sql` → **Run**
   - You should see "Success. No rows returned."

3. **Grab your API keys** (Project Settings → API):
   - `Project URL` → e.g. `https://abcd1234.supabase.co`
   - `anon public` key → for the dashboard (safe to expose; RLS protects data)
   - `service_role` key → for `run.py` only. **KEEP SECRET. Never put in the frontend.**

4. **Email confirmation (optional but smoother for solo use)**
   - Authentication → Providers → Email → consider turning **off** "Confirm email"
     so you can sign in immediately without the inbox round-trip. Fine for a private tool.

---

## Part 2 — Create your login + get your owner ID

1. Open the dashboard (see Part 3 for hosting, or just open `dashboard-supabase.html`
   locally in a browser to do this step).
2. First load asks for your **Project URL** and **anon key** → paste them in.
3. On the auth screen → **Create one** → sign up with your email + a password.
4. Back in Supabase → **Authentication → Users** → click your user → copy the **UID**.
   That's your `SUPABASE_OWNER_ID`.

---

## Part 3 — Host the dashboard (free)

Easiest is **Cloudflare Pages** or **Vercel**. Either works; pick one.

### Cloudflare Pages (drag-drop, no git needed)
1. https://pages.cloudflare.com → Create a project → **Direct Upload**
2. Drag in `dashboard-supabase.html` — but first **rename it to `index.html`**
   so it loads at the root URL.
3. Deploy → you get a URL like `cione-leads.pages.dev`. Bookmark it on your phone.

### Vercel (if you prefer)
1. Put `dashboard-supabase.html` (renamed `index.html`) in a folder
2. `npx vercel` from that folder, follow prompts, or drag-drop at vercel.com
3. Get your URL, bookmark it.

> Tip: To skip re-entering the URL/key each device, open `dashboard-supabase.html`
> and set `HARDCODED_URL` and `HARDCODED_KEY` (the anon key only) near the top of the
> `<script>`. Then the config screen is skipped. The anon key is safe to embed.

> Add to phone home screen: open the URL in Safari/Chrome → Share → "Add to Home Screen".
> It then behaves like an app.

---

## Part 4 — Load real leads

1. Fill in `config.py`:
   - `GOOGLE_PLACES_API_KEY` (required)
   - `APOLLO_API_KEY` (optional)
   - `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_OWNER_ID`
   - Set your `SEARCH_QUERIES` and `TARGET_LOCATIONS`
2. `pip install requests beautifulsoup4`
3. `python run.py`
   - Pulls leads → audits sites → (optional) enriches → writes CSV → pushes to Supabase
4. Open your hosted dashboard → leads are there, synced, sorted hottest-first.

You can also skip the script's DB push and just **import the CSV** from the dashboard's
upload zone — handy if you generate a list on one machine and load it from another.

---

## How you'll actually use it day to day

- Open the bookmarked URL on your phone.
- Hottest leads (most automation gaps) sit on top.
- Tap **copy** on an opener → paste into your email.
- Tap the phone number to call, email to mail.
- Set status as you go (New → Contacted → Replied → Meeting → Won/Dead).
- Add notes after calls. Everything syncs to every device instantly.
- Re-run `run.py` anytime to add new leads — duplicates merge, your statuses/notes stay.

---

## Files in this project

| File | What it is |
|------|-----------|
| `schema.sql` | Paste into Supabase SQL editor — creates the table + security |
| `dashboard-supabase.html` | The hosted app (rename to `index.html`) |
| `config.py` | Your keys + search targets |
| `run.py` | Run this to build + push leads |
| `places_fetch.py` | Google Places lead puller |
| `website_audit.py` | Generates the "why reach out" signals |
| `apollo_enrich.py` | Optional owner/email lookup |
| `supabase_push.py` | Pushes leads into Supabase |
| `dashboard.html` | The earlier browser-only version (no backend) — kept as a fallback |

---

## Security notes

- The **anon key** in the dashboard is fine to expose — Row Level Security means
  a user can only ever see their own rows.
- The **service_role key** in `config.py` bypasses RLS. Keep `config.py` off GitHub
  (add it to `.gitignore`) and never paste that key into the frontend.
- Each login only sees its own leads, so if you add a Cione teammate later they get
  their own isolated pipeline (or we can add a shared-team model down the road).
