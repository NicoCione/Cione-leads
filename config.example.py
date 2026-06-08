"""
Cione Solutions — Lead Gen Pipeline Config
Fill in your keys and target parameters here.
"""

# ── API KEYS ──────────────────────────────────────────────
# Get from: https://console.cloud.google.com (enable "Places API (New)")
GOOGLE_PLACES_API_KEY = "YOUR_GOOGLE_PLACES_KEY_HERE"

# Optional — get from https://apollo.io (free tier). Leave blank to skip enrichment.
APOLLO_API_KEY = ""

# ── SEARCH TARGETS ────────────────────────────────────────
# Each (query, location) pair becomes a search. Add as many as you want.
# The script tiles across these to get around the 60-result-per-search cap.
SEARCH_QUERIES = [
    "home remodeling contractor",
    "kitchen remodeling",
    "bathroom remodeling",
    "home restoration company",
    "general contractor residential",
]

# Cities/areas to target. Use specific cities for better coverage.
TARGET_LOCATIONS = [
    "Philadelphia, PA",
    "Pittsburgh, PA",
    "Allentown, PA",
    "Harrisburg, PA",
]

# How many results to pull per query+location combo (max 60 per Google's cap)
MAX_RESULTS_PER_SEARCH = 60

# ── SUPABASE (optional — for pushing leads to the dashboard DB) ──
# Leave blank to just write a CSV and skip the database push.
# Get these from Supabase → Project Settings → API.
SUPABASE_URL = ""
SUPABASE_SERVICE_KEY = ""      # paste your ROTATED service_role key here, locally — never in chat
# Your auth user's UUID (Supabase → Authentication → Users → your user → ID).
# Create your login in the dashboard first, then paste your user id here.
SUPABASE_OWNER_ID = ""

# ── OUTPUT ────────────────────────────────────────────────
OUTPUT_CSV = "cione_leads.csv"
PUSH_TO_SUPABASE = True   # set False to only write CSV
