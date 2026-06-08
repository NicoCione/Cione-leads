"""
apollo_enrich.py — Optional. Uses Apollo's free tier to find an
owner/manager name + email for each company (matched by domain).

Free tier note: email credits are generous but EXPORT is limited and
mobile credits are ~5/month. This pulls email-level data only.

If APOLLO_API_KEY is blank in config.py, this step is skipped entirely.
"""

import time
import requests
from urllib.parse import urlparse
from config import APOLLO_API_KEY

APOLLO_URL = "https://api.apollo.io/api/v1/mixed_people/search"

# Titles we care about for small remodeling cos — the decision makers
TARGET_TITLES = ["owner", "founder", "president", "ceo", "general manager",
                 "principal", "partner", "operations manager"]


def _domain_from_url(url):
    if not url:
        return ""
    if not url.startswith("http"):
        url = "http://" + url
    netloc = urlparse(url).netloc.lower()
    return netloc.replace("www.", "")


def enrich_lead(lead):
    """Try to find a decision-maker contact for one company via its domain."""
    domain = _domain_from_url(lead.get("website", ""))
    if not domain:
        return lead

    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "X-Api-Key": APOLLO_API_KEY,
    }
    body = {
        "q_organization_domains": domain,
        "person_titles": TARGET_TITLES,
        "page": 1,
        "per_page": 1,
    }

    try:
        resp = requests.post(APOLLO_URL, headers=headers, json=body, timeout=30)
        if resp.status_code != 200:
            print(f"  ! Apollo error {resp.status_code} for {domain}")
            return lead
        people = resp.json().get("people", [])
        if people:
            person = people[0]
            lead["contact_name"] = f"{person.get('first_name','')} {person.get('last_name','')}".strip()
            lead["contact_title"] = person.get("title", "")
            lead["contact_email"] = person.get("email", "")
            lead["contact_linkedin"] = person.get("linkedin_url", "")
    except Exception as e:
        print(f"  ! Apollo exception for {domain}: {e}")

    return lead


def enrich_all(leads):
    if not APOLLO_API_KEY:
        print("No Apollo key set — skipping contact enrichment.")
        return leads
    for i, lead in enumerate(leads, 1):
        print(f"Enriching {i}/{len(leads)}: {lead['name'][:40]} ...")
        enrich_lead(lead)
        time.sleep(0.6)
    return leads
