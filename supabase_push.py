"""
supabase_push.py — Push leads straight into your Supabase `leads` table
instead of (or in addition to) writing a CSV.

Uses the service_role key for server-side inserts (bypasses RLS, since
this runs on your machine, not in a browser). Keep that key secret —
never put it in the frontend.

Upserts on (owner_id, dedupe_key) so re-running updates rows instead of
creating duplicates.
"""

import requests
from config import (SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_OWNER_ID)


def _dedupe_key(lead):
    return f"{lead.get('name','')}|{lead.get('address','')}".lower().strip()


def push_leads(leads):
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY or not SUPABASE_OWNER_ID:
        print("Supabase not configured (URL / service key / owner id missing) — skipping push.")
        return False

    endpoint = f"{SUPABASE_URL}/rest/v1/leads"
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        # Upsert, merge duplicates on the unique (owner_id, dedupe_key) index
        "Prefer": "resolution=merge-duplicates,return=minimal",
    }

    payload = []
    for l in leads:
        payload.append({
            "owner_id": SUPABASE_OWNER_ID,
            "name": l.get("name", ""),
            "category": (l.get("category", "") or "").replace("_", " "),
            "phone": l.get("phone", ""),
            "website": l.get("website", ""),
            "address": l.get("address", ""),
            "rating": float(l["rating"]) if l.get("rating") else None,
            "review_count": int(l["review_count"]) if l.get("review_count") else None,
            "signal_count": l.get("signal_count", 0),
            "signal_flags": l.get("signal_flags", ""),
            "suggested_opener": l.get("suggested_opener", ""),
            "coaching_score": l.get("coaching_score", 0),
            "coaching_signals": l.get("coaching_signals", ""),
            "contact_name": l.get("contact_name", ""),
            "contact_title": l.get("contact_title", ""),
            "contact_email": l.get("contact_email", ""),
            "contact_linkedin": l.get("contact_linkedin", ""),
            "dedupe_key": _dedupe_key(l),
        })

    # Send in batches to stay well under request size limits
    CHUNK = 200
    pushed = 0
    for i in range(0, len(payload), CHUNK):
        batch = payload[i:i + CHUNK]
        params = {"on_conflict": "owner_id,dedupe_key"}
        resp = requests.post(endpoint, headers=headers, params=params, json=batch, timeout=60)
        if resp.status_code not in (200, 201, 204):
            print(f"  ! Supabase push error {resp.status_code}: {resp.text[:300]}")
            return False
        pushed += len(batch)
        print(f"  -> pushed {pushed}/{len(payload)}")

    print(f"Pushed {pushed} leads to Supabase.")
    return True
