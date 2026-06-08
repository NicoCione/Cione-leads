"""
website_audit.py — Visit each lead's website and detect tech-maturity /
automation-gap signals that give you a concrete reason to reach out.

Signals detected:
  - No SSL (http only)
  - Built on a DIY platform (Wix / Squarespace / Weebly / GoDaddy)
  - No live chat widget (Intercom, Drift, tawk.to, HubSpot, etc.)
  - No online booking / scheduling (Calendly, Acuity, etc.)
  - Plain contact form with no detectable CRM / tracking
  - No CRM or marketing pixel (HubSpot, Salesforce, Marketo)
  - Slow page load
  - No website at all (biggest signal of them all)

Each lead gets a list of flags + a generated opener line you can drop
straight into an email.
"""

import time
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# NOTE: This reads raw server-returned HTML. Tools loaded purely via
# heavy client-side JS (common on big enterprise sites) may not be detected,
# producing false "missing" flags. For small-business targets on simple
# sites (your actual ICP) this is rarely an issue, but spot-check the
# top results before sending so an opener never references a gap that
# isn't real.

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0 Safari/537.36"
}

# Fingerprints we look for in page HTML
CHAT_WIDGETS = ["intercom", "drift.com", "tawk.to", "hubspot", "livechat",
                "crisp.chat", "tidio", "zendesk", "freshchat", "olark"]
BOOKING_TOOLS = ["calendly", "acuityscheduling", "squarespace-scheduling",
                 "setmore", "youcanbook.me", "book now", "schedule online",
                 "housecallpro", "jobber"]
DIY_PLATFORMS = {"wix": "Wix", "squarespace": "Squarespace",
                 "weebly": "Weebly", "godaddy": "GoDaddy site builder",
                 "godaddysites": "GoDaddy site builder"}
CRM_PIXELS = ["hs-script", "hubspot", "salesforce", "marketo", "pardot",
              "google_tag_manager", "gtm.js"]


def audit_site(url):
    """Return (flags, opener) for a single website URL."""
    flags = []

    if not url:
        flags.append("No website listed on Google")
        return flags, "I noticed your business doesn't have a website listed — that's often the single biggest source of missed leads."

    # Normalize
    if not url.startswith("http"):
        url = "http://" + url

    parsed = urlparse(url)
    is_https = parsed.scheme == "https"

    try:
        start = time.time()
        resp = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        load_time = time.time() - start
        html = resp.text.lower()
        final_url = resp.url.lower()
    except Exception as e:
        flags.append(f"Website unreachable/erroring ({type(e).__name__})")
        return flags, "I tried to visit your site and it wouldn't load for me — that could be costing you customers who do the same."

    # SSL check (look at final URL after redirects)
    if not final_url.startswith("https"):
        flags.append("No SSL (insecure http)")

    # DIY platform check
    for token, label in DIY_PLATFORMS.items():
        if token in html or token in final_url:
            flags.append(f"Built on {label} (DIY platform)")
            break

    # Live chat check
    if not any(w in html for w in CHAT_WIDGETS):
        flags.append("No live chat widget")

    # Booking/scheduling check
    if not any(b in html for b in BOOKING_TOOLS):
        flags.append("No online booking/scheduling")

    # CRM / pixel check
    if not any(p in html for p in CRM_PIXELS):
        flags.append("No detectable CRM or tracking pixel")

    # Contact form check (form present but likely no automation)
    soup = BeautifulSoup(resp.text, "html.parser")
    has_form = bool(soup.find("form"))
    if has_form and not any(p in html for p in CRM_PIXELS):
        flags.append("Contact form with no detectable follow-up automation")

    # Load time
    if load_time > 5:
        flags.append(f"Slow site load ({load_time:.1f}s)")

    opener = _build_opener(flags)
    return flags, opener


def _build_opener(flags):
    """Turn the strongest flag into a natural email opener line."""
    if not flags:
        return "Your site looks solid — I had a different angle I wanted to run by you."

    # Priority order — lead with the most compelling gap
    if any("no follow-up automation" in f.lower() or "contact form" in f.lower() for f in flags):
        return "I noticed your site has a contact form but no automated follow-up behind it — that's usually where remodeling leads quietly slip away."
    if any("no online booking" in f.lower() for f in flags):
        return "I noticed there's no way to book or schedule directly from your site — adding that tends to capture leads who'd otherwise bounce."
    if any("no live chat" in f.lower() for f in flags):
        return "I noticed your site doesn't have a live chat or instant-response option — most homeowners reaching out expect a fast reply."
    if any("diy platform" in f.lower() for f in flags):
        return "I saw your site's on a DIY builder — totally fine to start, but it usually means lead capture and follow-up are still manual."
    if any("no detectable crm" in f.lower() for f in flags):
        return "From the outside it looks like lead tracking might still be manual on your end — that's exactly the kind of thing I help fix."
    return "I took a look at your site and spotted a couple of quick wins around how leads get captured and followed up."


def audit_all(leads):
    """Audit every lead and attach flags + opener + a numeric signal score."""
    for i, lead in enumerate(leads, 1):
        print(f"Auditing {i}/{len(leads)}: {lead['name'][:40]} ...")
        flags, opener = audit_site(lead.get("website", ""))
        lead["signal_flags"] = "; ".join(flags)
        lead["signal_count"] = len(flags)
        lead["suggested_opener"] = opener
        time.sleep(0.5)  # don't hammer sites
    return leads
