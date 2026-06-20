"""
NovaCare Health - KB Tier 0 Enhancement Script
Applies 3 fixes for better human self-service:
1. Convert text article references to clickable hyperlinks
2. Add "If this doesn't work" sections for edge cases
3. Pin featured articles to category pages

Usage: python enhance_kb_tier0.py
"""

import os
import re
import urllib3
import requests
from dotenv import load_dotenv

load_dotenv()

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
SUBDOMAIN = os.environ.get("ZENDESK_SUBDOMAIN", "novacarehealth-37424")
EMAIL = os.environ.get("ZENDESK_EMAIL")
API_TOKEN = os.environ.get("ZENDESK_API_TOKEN")
LOCALE = "en-us"
BASE_URL = f"https://{SUBDOMAIN}.zendesk.com"

AUTH = (f"{EMAIL}/token", API_TOKEN)
HEADERS = {"Content-Type": "application/json"}


# ============================================================================
# API Helpers
# ============================================================================

def api_get(path):
    r = requests.get(f"{BASE_URL}{path}", auth=AUTH, headers=HEADERS, verify=False)
    r.raise_for_status()
    return r.json()

def api_put(path, data):
    r = requests.put(f"{BASE_URL}{path}", auth=AUTH, headers=HEADERS, json=data, verify=False)
    r.raise_for_status()
    return r.json()


# ============================================================================
# FIX 1: Convert Text References to Hyperlinks
# ============================================================================

def get_all_articles():
    """Fetch all published articles."""
    print("\n[FIX 1] Fetching all articles...")
    articles = []
    page = 1
    while True:
        data = api_get(f"/api/v2/help_center/{LOCALE}/articles?page={page}&per_page=100")
        articles.extend(data.get("articles", []))
        if not data.get("next_page"):
            break
        page += 1
    print(f"  Found {len(articles)} articles")
    return articles


def build_title_to_url_map(articles):
    """Create mapping of article titles to their URLs."""
    return {
        art["title"]: f"{BASE_URL}/hc/{LOCALE}/articles/{art['id']}"
        for art in articles
    }


def add_cross_links(articles, title_map):
    """Replace text references with hyperlinks."""
    print("\n[FIX 1] Adding cross-article hyperlinks...")
    updated = 0
    
    for art in articles:
        body = art["body"]
        modified = False
        
        # Find patterns like "See <article title>" or "see our article on <title>"
        for title, url in title_map.items():
            if title == art["title"]:
                continue  # Skip self-references
            
            # Pattern 1: "See <em>How do I...</em>" or just "See How do I..."
            pattern1 = rf"(See|see)\s+(?:<em>)?({re.escape(title)})(?:</em>)?"
            if re.search(pattern1, body):
                replacement = rf'\1 <a href="{url}">\2</a>'
                body = re.sub(pattern1, replacement, body)
                modified = True
            
            # Pattern 2: Direct mention without "See"
            pattern2 = rf"(?<!>)({re.escape(title)})(?![^<]*</a>)"
            if re.search(pattern2, body) and '<a href=' not in body:
                replacement = rf'<a href="{url}">\1</a>'
                body = re.sub(pattern2, replacement, body, count=1)
                modified = True
        
        if modified:
            # Update article translation
            payload = {
                "translation": {
                    "title": art["title"],
                    "body": body,
                    "draft": False
                }
            }
            try:
                api_put(f"/api/v2/help_center/articles/{art['id']}/translations/{LOCALE}", payload)
                print(f"  ✅ Updated: {art['title'][:60]}")
                updated += 1
            except Exception as e:
                print(f"  ❌ Failed: {art['title'][:60]} - {str(e)[:50]}")
    
    print(f"  Total updated: {updated} articles")
    return updated


# ============================================================================
# FIX 2: Add "If This Doesn't Work" Sections
# ============================================================================

EDGE_CASE_SECTIONS = {
    "How do I verify my insurance is on file?": """
<h2>If Your Insurance Isn't Listed</h2>
<p>If you cannot find your insurance provider in the portal:</p>
<ul>
  <li>Contact our insurance verification team through the <strong>Help</strong> option in your patient portal</li>
  <li>Have your insurance card ready (front and back photos)</li>
  <li>We will manually verify your coverage within 24 hours</li>
</ul>
<p>Some smaller regional plans require manual verification — this is normal.</p>
""",
    "How do I reschedule my appointment?": """
<h2>If You Cannot Find a Suitable Time Slot</h2>
<p>If no available slots fit your schedule:</p>
<ul>
  <li>Join the <strong>waitlist</strong> — we will contact you if a slot opens due to a cancellation</li>
  <li>Contact our scheduling team through the <strong>Help</strong> option in the portal to discuss alternative options</li>
  <li>Consider a <strong>telehealth appointment</strong> if your provider offers video visits — these typically have more availability</li>
</ul>
""",
    "How do I book a new appointment?": """
<h2>If Online Booking Isn't Working</h2>
<p>If you encounter issues booking online:</p>
<ul>
  <li>Clear your browser cache and try again</li>
  <li>Try a different browser (Chrome, Firefox, Edge, Safari all supported)</li>
  <li>Contact our scheduling team through the <strong>Help</strong> option in the portal — we can book on your behalf</li>
</ul>
<p>Some providers do not accept online booking. If your provider is not listed, scheduling assistance is required.</p>
""",
    "How do I connect my device to the patient portal?": """
<h2>If the Connection Fails</h2>
<p><strong>Do not attempt further troubleshooting on your own.</strong> Contact our Device Support team through the <strong>Help</strong> option in your patient portal and select <strong>Clinical Device Issue</strong>.</p>
<p>Our certified specialists will guide you through the correct steps for your specific device model to ensure the connection is set up safely and accurately.</p>
"""
}


def add_edge_case_sections(articles):
    """Add 'If this doesn't work' sections to specific articles."""
    print("\n[FIX 2] Adding edge case handling sections...")
    updated = 0
    
    for art in articles:
        if art["title"] not in EDGE_CASE_SECTIONS:
            continue
        
        body = art["body"]
        
        # Check if section already exists
        if "If" in body and ("doesn't work" in body.lower() or "isn't listed" in body.lower()):
            print(f"  ⏭️  Skipped (already has edge case): {art['title'][:60]}")
            continue
        
        # Append before any "Related Articles" or at the end
        edge_section = EDGE_CASE_SECTIONS[art["title"]]
        
        if "<h2>Related Articles</h2>" in body:
            body = body.replace("<h2>Related Articles</h2>", f"{edge_section}\n<h2>Related Articles</h2>")
        else:
            body = body.rstrip() + f"\n\n{edge_section}"
        
        # Update article
        payload = {
            "translation": {
                "title": art["title"],
                "body": body,
                "draft": False
            }
        }
        try:
            api_put(f"/api/v2/help_center/articles/{art['id']}/translations/{LOCALE}", payload)
            print(f"  ✅ Updated: {art['title'][:60]}")
            updated += 1
        except Exception as e:
            print(f"  ❌ Failed: {art['title'][:60]} - {str(e)[:50]}")
    
    print(f"  Total updated: {updated} articles")
    return updated


# ============================================================================
# FIX 3: Promote Featured Articles (Position-Based)
# ============================================================================

def get_sections():
    """Fetch all sections."""
    print("\n[FIX 3] Fetching sections...")
    sections = []
    page = 1
    while True:
        data = api_get(f"/api/v2/help_center/{LOCALE}/sections?page={page}&per_page=100")
        sections.extend(data.get("sections", []))
        if not data.get("next_page"):
            break
        page += 1
    print(f"  Found {len(sections)} sections")
    return sections


def promote_featured_articles(articles, sections):
    """Promote key articles to top of their sections."""
    print("\n[FIX 3] Promoting featured articles...")
    
    # Define which articles should be featured (top of section)
    FEATURED = [
        "How do I dispute a charge on my bill?",
        "How do I reschedule my appointment?",
        "How do I verify my insurance is on file?",
        "My device is showing an error — what should I do?"
    ]
    
    # Build section_id -> articles map
    section_articles = {}
    for art in articles:
        sid = art["section_id"]
        if sid not in section_articles:
            section_articles[sid] = []
        section_articles[sid].append(art)
    
    updated = 0
    for section_id, arts in section_articles.items():
        # Find featured articles in this section
        featured = [a for a in arts if a["title"] in FEATURED]
        non_featured = [a for a in arts if a["title"] not in FEATURED]
        
        if not featured:
            continue
        
        # Reorder: featured first, then others
        ordered = featured + non_featured
        
        # Update position for each article
        for position, art in enumerate(ordered, start=1):
            payload = {"article": {"position": position}}
            try:
                api_put(f"/api/v2/help_center/articles/{art['id']}", payload)
            except Exception as e:
                print(f"  ⚠️  Position update failed for {art['title'][:50]}")
        
        print(f"  ✅ Promoted {len(featured)} article(s) in section {section_id}")
        updated += len(featured)
    
    print(f"  Total promoted: {updated} articles")
    return updated


# ============================================================================
# Main
# ============================================================================

def run():
    print(f"\n{'='*60}")
    print(f"NovaCare Health - KB Tier 0 Enhancements")
    print(f"Instance: {BASE_URL}")
    print(f"{'='*60}")
    
    # Fetch data
    articles = get_all_articles()
    sections = get_sections()
    
    # Apply fixes
    title_map = build_title_to_url_map(articles)
    fix1_count = add_cross_links(articles, title_map)
    
    # Refresh articles after Fix 1 updates
    articles = get_all_articles()
    fix2_count = add_edge_case_sections(articles)
    
    # Refresh again after Fix 2
    articles = get_all_articles()
    fix3_count = promote_featured_articles(articles, sections)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"ENHANCEMENTS COMPLETE")
    print(f"{'='*60}")
    print(f"  ✅ Fix 1 (Cross-links):       {fix1_count} articles")
    print(f"  ✅ Fix 2 (Edge cases):        {fix2_count} articles")
    print(f"  ✅ Fix 3 (Featured articles): {fix3_count} articles")
    print(f"\n  View your Help Center: {BASE_URL}/hc/{LOCALE}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run()
