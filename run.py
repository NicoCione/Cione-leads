"""
run.py — Cione Solutions lead gen pipeline.

Pipeline:
  1. Pull remodeling/restoration leads from Google Places
  2. Audit each lead's website for automation-gap signals
  3. (Optional) Enrich with owner/manager contact via Apollo
  4. Sort by signal strength and write a clean CSV

Usage:
  1. Fill in config.py (at minimum GOOGLE_PLACES_API_KEY)
  2. python run.py
"""

import csv
from config import (SEARCH_QUERIES, TARGET_LOCATIONS, OUTPUT_CSV,
                    GOOGLE_PLACES_API_KEY)
from places_fetch import fetch_all
from website_audit import audit_all
from apollo_enrich import enrich_all

CSV_FIELDS = [
    "name", "contact_name", "contact_title", "contact_email", "contact_linkedin",
    "phone", "website", "address", "rating", "review_count",
    "signal_count", "signal_flags", "suggested_opener",
    "coaching_score", "coaching_signals",
    "category", "search_query", "search_location", "business_status",
]


def main():
    if GOOGLE_PLACES_API_KEY == "YOUR_GOOGLE_PLACES_KEY_HERE":
        print("ERROR: Set your GOOGLE_PLACES_API_KEY in config.py first.")
        return

    print("=" * 60)
    print("STEP 1 — Fetching leads from Google Places")
    print("=" * 60)
    leads = fetch_all(SEARCH_QUERIES, TARGET_LOCATIONS)
    print(f"\nTotal unique leads: {len(leads)}\n")

    print("=" * 60)
    print("STEP 2 — Auditing websites for outreach signals")
    print("=" * 60)
    leads = audit_all(leads)

    print("\n" + "=" * 60)
    print("STEP 3 — Enriching contacts (Apollo, if configured)")
    print("=" * 60)
    leads = enrich_all(leads)

    # Ensure every row has all fields
    for lead in leads:
        for f in CSV_FIELDS:
            lead.setdefault(f, "")

    # Sort: coaching-group members first (primed to buy), then by signal count.
    # Net effect: "in a coaching group AND has lots of gaps" rises to the top.
    leads.sort(key=lambda x: (x.get("coaching_score", 0), x.get("signal_count", 0)), reverse=True)

    print("\n" + "=" * 60)
    print(f"STEP 4 — Writing {OUTPUT_CSV}")
    print("=" * 60)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(leads)

    print(f"\nCSV written: {OUTPUT_CSV} ({len(leads)} leads)")

    # Step 5 — optional push to Supabase
    try:
        from config import PUSH_TO_SUPABASE
        if PUSH_TO_SUPABASE:
            print("\n" + "=" * 60)
            print("STEP 5 — Pushing to Supabase")
            print("=" * 60)
            from supabase_push import push_leads
            push_leads(leads)
    except ImportError:
        pass

    print("\nDone. Top targets (most automation gaps) are at the top.")


if __name__ == "__main__":
    main()
