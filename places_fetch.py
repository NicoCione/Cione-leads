"""
places_fetch.py — Pull business leads from Google Places API (New).

Uses the Text Search endpoint. Returns name, address, phone, website,
rating, and review count for each business.

Google caps Text Search at 60 results (20/page x 3 pages), so we tile
across multiple query+location combos defined in config.py to widen coverage.
"""

import time
import requests
from config import GOOGLE_PLACES_API_KEY, MAX_RESULTS_PER_SEARCH

PLACES_URL = "https://places.googleapis.com/v1/places:searchText"

# Field mask controls what data (and what billing tier) you get back.
# These fields keep you in the cheaper Pro/Essentials tiers where possible.
FIELD_MASK = ",".join([
    "places.displayName",
    "places.formattedAddress",
    "places.nationalPhoneNumber",
    "places.internationalPhoneNumber",
    "places.websiteUri",
    "places.rating",
    "places.userRatingCount",
    "places.businessStatus",
    "places.primaryType",
    "nextPageToken",
])


def search_places(query, location, max_results=MAX_RESULTS_PER_SEARCH):
    """Run a single text search, paginating up to max_results."""
    results = []
    page_token = None
    full_query = f"{query} in {location}"

    while len(results) < max_results:
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
            "X-Goog-FieldMask": FIELD_MASK,
        }
        body = {"textQuery": full_query, "pageSize": 20}
        if page_token:
            body["pageToken"] = page_token

        resp = requests.post(PLACES_URL, headers=headers, json=body, timeout=30)
        if resp.status_code != 200:
            print(f"  ! Error {resp.status_code} for '{full_query}': {resp.text[:200]}")
            break

        data = resp.json()
        places = data.get("places", [])
        for p in places:
            results.append({
                "name": p.get("displayName", {}).get("text", ""),
                "address": p.get("formattedAddress", ""),
                "phone": p.get("nationalPhoneNumber", "") or p.get("internationalPhoneNumber", ""),
                "website": p.get("websiteUri", ""),
                "rating": p.get("rating", ""),
                "review_count": p.get("userRatingCount", ""),
                "business_status": p.get("businessStatus", ""),
                "category": p.get("primaryType", ""),
                "search_query": query,
                "search_location": location,
            })

        page_token = data.get("nextPageToken")
        if not page_token:
            break
        # Google requires a short delay before the next page token is valid
        time.sleep(2)

    return results[:max_results]


def fetch_all(queries, locations):
    """Run every query x location combo and dedupe by name+address."""
    all_results = []
    seen = set()

    for location in locations:
        for query in queries:
            print(f"Searching: '{query}' in {location} ...")
            batch = search_places(query, location)
            for r in batch:
                key = (r["name"].lower().strip(), r["address"].lower().strip())
                if key not in seen and r["name"]:
                    seen.add(key)
                    all_results.append(r)
            print(f"  -> {len(batch)} found, {len(all_results)} unique so far")
            time.sleep(0.5)  # be polite to the API

    return all_results
