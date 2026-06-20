"""
NovaCare Health - Zendesk Knowledge Base Seeder
Creates all Help Center categories, sections, and articles via Zendesk API.

Usage:
    1. Add to .env:
       ZENDESK_EMAIL=your-email@example.com
       ZENDESK_API_TOKEN=your-api-token
       ZENDESK_SUBDOMAIN=novacarehealth-37424
    2. Run: python seed_kb_articles.py
"""

import os
import sys
import json
import urllib3
import requests
from time import sleep
from dotenv import load_dotenv

# Suppress SSL warnings — Windows Python (Store) doesn't trust local CA chain
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

# ============================================================================
# Configuration
# ============================================================================

SUBDOMAIN = os.environ.get("ZENDESK_SUBDOMAIN", "novacarehealth-37424")
EMAIL = os.environ.get("ZENDESK_EMAIL")
API_TOKEN = os.environ.get("ZENDESK_API_TOKEN")
LOCALE = "en-us"
BASE_URL = f"https://{SUBDOMAIN}.zendesk.com"

if not EMAIL or not API_TOKEN:
    print("ERROR: Set ZENDESK_EMAIL and ZENDESK_API_TOKEN in your .env file")
    sys.exit(1)

AUTH = (f"{EMAIL}/token", API_TOKEN)
HEADERS = {"Content-Type": "application/json"}


# ============================================================================
# API Helpers
# ============================================================================

def api_get(path):
    r = requests.get(f"{BASE_URL}{path}", auth=AUTH, headers=HEADERS, verify=False)
    r.raise_for_status()
    return r.json()

def api_post(path, data):
    r = requests.post(f"{BASE_URL}{path}", auth=AUTH, headers=HEADERS, json=data, verify=False)
    if r.status_code not in (200, 201):
        print(f"  ERROR {r.status_code}: {r.text[:200]}")
        return None
    return r.json()

def get_permission_group_id():
    """Get the first available permission group (Staff/Everyone)."""
    data = api_get("/api/v2/guide/permission_groups")
    groups = data.get("permission_groups", [])
    if not groups:
        print("ERROR: No permission groups found. Enable Guide in your instance.")
        sys.exit(1)
    # Prefer "Staff" group or fall back to first available
    for g in groups:
        if "staff" in g["name"].lower() or "managers" in g["name"].lower():
            print(f"  Using permission group: {g['name']} (id={g['id']})")
            return g["id"]
    print(f"  Using permission group: {groups[0]['name']} (id={groups[0]['id']})")
    return groups[0]["id"]


# ============================================================================
# Content Definition
# ============================================================================

STRUCTURE = [
    {
        "name": "Billing and Payments",
        "description": "Information about your medical bills, payment options, and billing disputes.",
        "sections": [
            {
                "name": "Understanding Your Bill",
                "description": "How to read and interpret your NovaCare Health bill.",
                "articles": [
                    {
                        "title": "How do I understand my medical bill?",
                        "description": "Your bill shows services received, what insurance paid, and your remaining balance. Here is how to read each section.",
                        "body": """
<p>Your NovaCare Health bill is divided into three sections. Understanding each one helps you verify charges and know exactly what you owe.</p>

<h2>1. Services Provided</h2>
<p>Lists every service from your visit:</p>
<ul>
  <li>Date of service</li>
  <li>Provider name</li>
  <li>Procedure or test name</li>
  <li>Amount billed before insurance</li>
</ul>

<h2>2. Insurance Payment</h2>
<p>Shows what your insurance plan paid and any adjustments applied. Compare this with your Explanation of Benefits (EOB) from your insurer to verify the amounts match.</p>

<h2>3. Your Balance</h2>
<p>The amount you owe after insurance, which may include:</p>
<ul>
  <li><strong>Copay</strong> — fixed amount per visit (e.g., $25)</li>
  <li><strong>Coinsurance</strong> — your percentage after deductible (e.g., 20%)</li>
  <li><strong>Deductible</strong> — amount you pay before insurance coverage begins</li>
</ul>

<h2>Questions About a Charge?</h2>
<p>If a charge looks incorrect, you can dispute it through your patient portal. See <em>How do I dispute a charge on my bill?</em> for steps.</p>
"""
                    }
                ]
            },
            {
                "name": "Managing Payments",
                "description": "Payment methods, plans, disputes, and autopay options.",
                "articles": [
                    {
                        "title": "What payment methods do you accept?",
                        "description": "Pay online, by phone, or by mail using credit card, debit card, HSA/FSA card, or bank transfer.",
                        "body": """
<p>NovaCare Health accepts multiple payment methods to make settling your account as convenient as possible.</p>

<h2>Online (Fastest)</h2>
<p>Sign in to your patient portal and go to <strong>Billing → Make a Payment</strong>:</p>
<ul>
  <li>Credit or debit card (Visa, Mastercard, Amex, Discover)</li>
  <li>Health Savings Account (HSA) or Flexible Spending Account (FSA) card</li>
  <li>Bank transfer (ACH) — no processing fee</li>
</ul>
<p>Payments post within 24 hours and a receipt is emailed automatically.</p>

<h2>By Phone</h2>
<p>Call our billing team through the <strong>Help</strong> option in your patient portal, Monday–Friday 8 AM–6 PM. Have your account number and payment details ready.</p>

<h2>By Mail</h2>
<p>Send a check or money order with your account number written on the memo line. Mailing address is printed on your paper bill. Allow 7–10 business days for processing.</p>

<h2>Need More Time to Pay?</h2>
<p>See <em>How do I set up a payment plan?</em> if you need to spread your balance over time.</p>
"""
                    },
                    {
                        "title": "How do I dispute a charge on my bill?",
                        "description": "Submit a billing dispute through your patient portal. Disputed amounts are paused during review — we investigate and respond within 14 business days.",
                        "body": """
<p>If you believe a charge on your bill is incorrect, submit a dispute through your patient portal. Collection activity is paused on disputed amounts while we investigate.</p>

<h2>Submit a Dispute Online</h2>
<ol>
  <li>Sign in to your patient portal</li>
  <li>Go to <strong>Billing → View Bills</strong></li>
  <li>Select the bill containing the disputed charge</li>
  <li>Click <strong>Dispute This Charge</strong> next to the item</li>
  <li>Describe the issue and submit</li>
</ol>
<p>You will receive a confirmation email with a dispute reference number within one hour.</p>

<h2>What to Expect After Submitting</h2>
<ul>
  <li><strong>Day 1–2:</strong> Acknowledgment email with reference number</li>
  <li><strong>Day 3–10:</strong> Billing team reviews your account and insurance records</li>
  <li><strong>Day 11–14:</strong> Resolution — charge corrected or explanation provided</li>
</ul>
<p>Collection activity is paused on disputed amounts during this entire period.</p>

<h2>Common Reasons to Dispute</h2>
<ul>
  <li>Charged for a service not received</li>
  <li>Duplicate charge for the same visit</li>
  <li>Insurance payment not applied to your account</li>
  <li>Incorrect date of service on the bill</li>
</ul>

<h2>Cannot Access the Portal?</h2>
<p>Use the <strong>Help</strong> option in your patient portal, or raise a new support request and select <em>Billing Dispute</em> as the topic.</p>
"""
                    },
                    {
                        "title": "How do I set up a payment plan?",
                        "description": "You can spread your balance over monthly installments through your patient portal. No interest is charged on approved payment plans.",
                        "body": """
<p>If you cannot pay your full balance at once, NovaCare Health offers interest-free payment plans through your patient portal.</p>

<h2>Set Up a Payment Plan</h2>
<ol>
  <li>Sign in to your patient portal</li>
  <li>Go to <strong>Billing → Payment Plans</strong></li>
  <li>Select the balance you want to put on a plan</li>
  <li>Choose your monthly payment amount (minimum $25/month)</li>
  <li>Select a payment method for automatic monthly deductions</li>
  <li>Review and confirm</li>
</ol>
<p>Plans are approved instantly for balances under $2,000. Larger balances are reviewed within 2 business days.</p>

<h2>Plan Terms</h2>
<ul>
  <li><strong>No interest</strong> — you pay only what you owe</li>
  <li><strong>Minimum payment:</strong> $25 per month</li>
  <li><strong>Maximum term:</strong> 24 months</li>
  <li>Automatic payment on the same date each month</li>
</ul>

<h2>Modifying or Cancelling a Plan</h2>
<p>Go to <strong>Billing → Payment Plans → Manage Plan</strong> to change your payment amount, update your payment method, or cancel the plan. Changes take effect the following billing cycle.</p>

<h2>Financial Assistance</h2>
<p>If you are experiencing financial hardship, contact our billing team through the <strong>Help</strong> option in your patient portal to discuss financial assistance options.</p>
"""
                    },
                    {
                        "title": "What is a copay and why was I charged one?",
                        "description": "A copay is a fixed amount your insurance plan requires you to pay at the time of each visit. It is defined by your insurance policy, not by NovaCare.",
                        "body": """
<p>A copay (or co-payment) is a fixed dollar amount you pay at the time of a healthcare visit, as defined by your insurance policy.</p>

<h2>How Copays Work</h2>
<ul>
  <li>Your insurance sets the copay amount — NovaCare does not determine it</li>
  <li>Common copay amounts: $20–$50 for a primary care visit; $50–$150 for a specialist</li>
  <li>Copays apply regardless of whether you have met your deductible</li>
  <li>Some services (e.g., preventive care) may have a $0 copay under your plan</li>
</ul>

<h2>Copay vs. Coinsurance</h2>
<ul>
  <li><strong>Copay:</strong> Fixed amount per visit (e.g., $30 every time you see your doctor)</li>
  <li><strong>Coinsurance:</strong> Percentage of the cost after your deductible (e.g., you pay 20%, insurance pays 80%)</li>
</ul>
<p>Your bill may include both depending on the services received.</p>

<h2>If Your Copay Looks Wrong</h2>
<p>Compare the amount on your bill with your insurance card or your plan's Summary of Benefits. If there is a discrepancy, contact your insurance company first — they determine the copay amount. If the issue is with how NovaCare applied the payment, use <em>How do I dispute a charge on my bill?</em>.</p>
"""
                    }
                ]
            }
        ]
    },
    {
        "name": "Appointments",
        "description": "Scheduling, rescheduling, cancellations, and telehealth appointments.",
        "sections": [
            {
                "name": "Changes and Cancellations",
                "description": "How to reschedule or cancel appointments and our no-show policy.",
                "articles": [
                    {
                        "title": "How do I reschedule my appointment?",
                        "description": "Reschedule through your patient portal anytime, or contact our scheduling team. Changes made 24+ hours in advance are free of charge.",
                        "body": """
<p>You can reschedule your appointment through your patient portal at any time, 24 hours a day.</p>

<h2>Reschedule Online</h2>
<ol>
  <li>Sign in to your patient portal</li>
  <li>Go to <strong>Appointments → Upcoming</strong></li>
  <li>Select the appointment you want to change</li>
  <li>Click <strong>Reschedule</strong></li>
  <li>Choose a new date and time from available slots</li>
  <li>Confirm — you will receive an email and SMS confirmation</li>
</ol>

<h2>Rescheduling Timeframes</h2>
<ul>
  <li><strong>24+ hours before appointment:</strong> Free, no restrictions</li>
  <li><strong>Less than 24 hours before:</strong> $25 change fee may apply</li>
  <li><strong>Same-day changes:</strong> Subject to provider availability</li>
</ul>

<h2>Cannot Find a Suitable Slot?</h2>
<p>If your provider has no available slots in the timeframe you need:</p>
<ul>
  <li>Request to join the <strong>waitlist</strong> — we will contact you if a slot opens</li>
  <li>See another provider in the same specialty by selecting a different provider in the portal</li>
  <li>Contact our scheduling team through the <strong>Help</strong> option in your portal</li>
</ul>
"""
                    },
                    {
                        "title": "What is your cancellation and no-show policy?",
                        "description": "Cancel 24+ hours ahead at no charge. Same-day cancellations incur a $25 fee. No-shows incur a $50 fee.",
                        "body": """
<p>We understand that plans change. Here is what you need to know about cancelling your appointment.</p>

<h2>Cancellation Fees</h2>
<ul>
  <li><strong>24+ hours before appointment:</strong> No fee — cancel anytime through the patient portal</li>
  <li><strong>Less than 24 hours before:</strong> $25 cancellation fee</li>
  <li><strong>No-show (missed without cancelling):</strong> $50 no-show fee</li>
</ul>
<p>Fees are added to your account balance and appear on your next bill.</p>

<h2>How to Cancel</h2>
<ol>
  <li>Sign in to your patient portal</li>
  <li>Go to <strong>Appointments → Upcoming</strong></li>
  <li>Select the appointment</li>
  <li>Click <strong>Cancel Appointment</strong> and confirm</li>
</ol>
<p>You will receive a cancellation confirmation by email.</p>

<h2>Fee Waivers</h2>
<p>Cancellation and no-show fees may be waived for:</p>
<ul>
  <li>Medical emergencies — contact us as soon as possible through the portal</li>
  <li>Sudden illness on the day of the appointment</li>
  <li>Provider-initiated cancellations — NovaCare never charges if we cancel your appointment</li>
</ul>
<p>To request a fee waiver, raise a support request and select <em>Cancellation Fee Waiver</em>.</p>

<h2>Consider Rescheduling Instead</h2>
<p>If you still need care, reschedule rather than cancel. See <em>How do I reschedule my appointment?</em></p>
"""
                    }
                ]
            },
            {
                "name": "Scheduling",
                "description": "Booking new appointments and telehealth options.",
                "articles": [
                    {
                        "title": "How do I book a new appointment?",
                        "description": "Book appointments online through your patient portal, available 24/7. Choose your provider, specialty, date, and appointment type in a few steps.",
                        "body": """
<p>Book appointments with your NovaCare Health providers directly through your patient portal — no phone call needed.</p>

<h2>Book Online</h2>
<ol>
  <li>Sign in to your patient portal</li>
  <li>Go to <strong>Appointments → Book an Appointment</strong></li>
  <li>Select appointment type: <em>In-person</em> or <em>Telehealth (video)</em></li>
  <li>Choose your provider or browse by specialty</li>
  <li>Select a date and time from available slots</li>
  <li>Add any notes for your provider (optional)</li>
  <li>Confirm — you will receive confirmation by email and SMS</li>
</ol>

<h2>Appointment Types Available Online</h2>
<ul>
  <li>Primary care and follow-up visits</li>
  <li>Specialist consultations</li>
  <li>Telehealth video visits</li>
  <li>Annual wellness checks</li>
  <li>Lab result reviews</li>
</ul>

<h2>Telehealth Appointments</h2>
<p>Video visits work the same as in-person bookings — select <em>Telehealth</em> when choosing appointment type. You will receive a secure video link 24 hours before your appointment. You do not need to download any additional software.</p>

<h2>Do Not See Your Provider?</h2>
<p>Not all providers accept online booking. Contact our scheduling team through the <strong>Help</strong> option in the portal to book on your behalf.</p>
"""
                    }
                ]
            }
        ]
    },
    {
        "name": "Insurance",
        "description": "Verifying coverage, updating insurance information, and understanding pre-authorization.",
        "sections": [
            {
                "name": "Coverage and Verification",
                "description": "How to verify and update your insurance information.",
                "articles": [
                    {
                        "title": "How do I verify my insurance is on file?",
                        "description": "Check your insurance status anytime through your patient portal under Profile → Insurance. Verification takes 24–48 hours after you update your details.",
                        "body": """
<p>Verify your insurance information is current before your appointment to avoid unexpected out-of-pocket charges.</p>

<h2>Check Your Insurance Status</h2>
<ol>
  <li>Sign in to your patient portal</li>
  <li>Go to <strong>Profile → Insurance Information</strong></li>
  <li>Review the details on file:
    <ul>
      <li>Insurance company name</li>
      <li>Member/Subscriber ID</li>
      <li>Group number</li>
      <li>Coverage status (Active / Inactive / Pending verification)</li>
    </ul>
  </li>
</ol>

<h2>Update Your Insurance</h2>
<p>If your insurance has changed or the details are incorrect:</p>
<ol>
  <li>Go to <strong>Profile → Insurance Information → Update Insurance</strong></li>
  <li>Upload a photo of the front and back of your insurance card</li>
  <li>Submit — verification takes 24–48 hours</li>
  <li>You will receive an email when verification is complete</li>
</ol>

<h2>What We Verify</h2>
<ul>
  <li>Policy is currently active</li>
  <li>NovaCare Health is in your plan's network</li>
  <li>Any referral or pre-authorization requirements for your appointment type</li>
</ul>

<h2>Insurance Not Accepted?</h2>
<p>If your plan is not accepted, we offer self-pay rates and payment plan options. Contact our billing team through the <strong>Help</strong> option in the portal for details.</p>
"""
                    },
                    {
                        "title": "What is pre-authorization and do I need it?",
                        "description": "Pre-authorization is approval from your insurance company required before certain procedures. Check if your upcoming appointment needs it to avoid claim denials.",
                        "body": """
<p>Pre-authorization (also called prior authorization) is a requirement from some insurance plans to approve certain services before they are performed. Without it, your insurer may deny the claim and leave you responsible for the full cost.</p>

<h2>Which Services Typically Require Pre-Authorization?</h2>
<ul>
  <li>Specialist referrals (for some HMO plans)</li>
  <li>Elective surgeries and procedures</li>
  <li>Advanced imaging (MRI, CT scans)</li>
  <li>Certain medications or therapies</li>
  <li>Extended hospital stays</li>
</ul>
<p>Routine office visits and preventive care generally do not require pre-authorization.</p>

<h2>How to Check If You Need Pre-Authorization</h2>
<ol>
  <li>Call the Member Services number on the back of your insurance card</li>
  <li>Provide the procedure code (your NovaCare provider can give you this)</li>
  <li>Ask if pre-authorization is required and, if so, what documentation is needed</li>
</ol>

<h2>NovaCare's Role</h2>
<p>For procedures we schedule on your behalf, our clinical team submits pre-authorization requests directly to your insurer when required. You will be notified of the outcome before your appointment.</p>
<p>If you are unsure whether your upcoming appointment needs authorization, contact our insurance team through the <strong>Help</strong> option in the patient portal.</p>
"""
                    }
                ]
            }
        ]
    },
    {
        "name": "Clinical Devices",
        "description": "Support for medical devices including glucose monitors and blood pressure cuffs.",
        "sections": [
            {
                "name": "Device Support",
                "description": "Contact our certified device specialists for all device issues. Do not attempt to self-troubleshoot clinical devices.",
                "articles": [
                    {
                        "title": "My device is showing an error — what should I do?",
                        "description": "Stop using the device and contact our certified Device Support team immediately. Do not attempt to reset or repair the device yourself.",
                        "body": """
<p><strong>Important:</strong> Clinical devices used to monitor your health are regulated medical equipment. If your device shows an error, do not attempt to troubleshoot or repair it yourself.</p>

<h2>What to Do Right Now</h2>
<ol>
  <li><strong>Stop using the device immediately</strong></li>
  <li>Note the exact error code or message displayed</li>
  <li>Note what you were doing when the error appeared</li>
  <li>Contact our Device Support team (see below)</li>
</ol>

<h2>Contact Device Support</h2>
<p>Our certified device specialists are available to help:</p>
<ul>
  <li>Raise a support request through your patient portal and select <strong>Clinical Device Issue</strong></li>
  <li>In urgent situations, use the <strong>Live Chat</strong> option in the portal and indicate it is a device emergency</li>
</ul>
<p>Have the following ready when you contact us:</p>
<ul>
  <li>Device model name and model number (printed on the device or packaging)</li>
  <li>Serial number (on the back of the device or under the battery cover)</li>
  <li>The exact error code or description of what is happening</li>
</ul>

<h2>Why You Must Not Self-Troubleshoot</h2>
<ul>
  <li>Incorrect repairs may affect reading accuracy and impact your treatment</li>
  <li>Unauthorized modifications void the manufacturer warranty</li>
  <li>FDA-regulated devices require certified specialist assessment</li>
</ul>

<h2>While You Wait for Support</h2>
<p>If you need a reading urgently and your device is not working:</p>
<ul>
  <li>Many pharmacies offer free blood pressure and glucose checks</li>
  <li>Contact your provider's office to arrange an in-clinic measurement</li>
  <li>Do not make treatment decisions (such as insulin dosing) without a verified reading</li>
</ul>
""",
                        "label_names": ["clinical-device"]
                    },
                    {
                        "title": "How do I connect my device to the patient portal?",
                        "description": "Sync your glucose monitor or blood pressure cuff to your patient portal to share readings with your care team. Contact Device Support if the connection fails.",
                        "body": """
<p>Connecting your device to the patient portal allows your care team to monitor your readings between appointments and respond quickly if values are outside your target range.</p>

<h2>Before You Start</h2>
<ul>
  <li>Ensure your device is fully charged</li>
  <li>Download or update the NovaCare Health mobile app on your phone</li>
  <li>Enable Bluetooth on your phone</li>
  <li>Keep the device within 3 feet of your phone during pairing</li>
</ul>

<h2>Connect Your Device</h2>
<ol>
  <li>Open the NovaCare Health app</li>
  <li>Tap <strong>Devices → Add Device</strong></li>
  <li>Select your device type (glucose monitor, blood pressure cuff, etc.)</li>
  <li>Follow the on-screen pairing instructions</li>
  <li>Once paired, tap <strong>Sync Now</strong> to upload your recent readings</li>
</ol>
<p>Readings will appear in your patient portal under <strong>Health Data → Device Readings</strong> within a few minutes.</p>

<h2>If the Connection Fails</h2>
<p><strong>Do not attempt further troubleshooting on your own.</strong> Contact our Device Support team through the <strong>Help</strong> option in your patient portal and select <strong>Clinical Device Issue</strong>.</p>
<p>Our certified specialists will guide you through the correct steps for your specific device model to ensure the connection is set up safely and accurately.</p>
""",
                        "label_names": ["clinical-device"]
                    }
                ]
            }
        ]
    }
]


# ============================================================================
# Seeder Logic
# ============================================================================

def run():
    print(f"\n{'='*60}")
    print(f"NovaCare Health - Zendesk KB Seeder")
    print(f"Instance: {BASE_URL}")
    print(f"{'='*60}\n")

    # Get permission group ID
    print("Fetching permission groups...")
    perm_group_id = get_permission_group_id()

    created = {"categories": 0, "sections": 0, "articles": 0}
    failed = []

    for cat_data in STRUCTURE:
        # ── Create Category ─────────────────────────────────────────
        print(f"\n[CATEGORY] {cat_data['name']}")
        cat_payload = {
            "category": {
                "name": cat_data["name"],
                "description": cat_data["description"],
                "locale": LOCALE
            }
        }
        cat_result = api_post(f"/api/v2/help_center/{LOCALE}/categories", cat_payload)
        if not cat_result:
            failed.append(f"Category: {cat_data['name']}")
            continue

        cat_id = cat_result["category"]["id"]
        print(f"  ✅ Created category id={cat_id}")
        created["categories"] += 1
        sleep(0.3)

        for sec_data in cat_data.get("sections", []):
            # ── Create Section ─────────────────────────────────────
            print(f"\n  [SECTION] {sec_data['name']}")
            sec_payload = {
                "section": {
                    "name": sec_data["name"],
                    "description": sec_data["description"],
                    "locale": LOCALE
                }
            }
            sec_result = api_post(
                f"/api/v2/help_center/{LOCALE}/categories/{cat_id}/sections",
                sec_payload
            )
            if not sec_result:
                failed.append(f"Section: {sec_data['name']}")
                continue

            sec_id = sec_result["section"]["id"]
            print(f"    ✅ Created section id={sec_id}")
            created["sections"] += 1
            sleep(0.3)

            for art_data in sec_data.get("articles", []):
                # ── Create Article ─────────────────────────────────
                print(f"\n    [ARTICLE] {art_data['title']}")
                art_payload = {
                    "article": {
                        "title": art_data["title"],
                        "body": art_data["body"].strip(),
                        "locale": LOCALE,
                        "draft": False,
                        "user_segment_id": None,
                        "permission_group_id": perm_group_id,
                        "label_names": art_data.get("label_names", [])
                    }
                }

                # Set description via translation (Zendesk stores it separately)
                art_result = api_post(
                    f"/api/v2/help_center/{LOCALE}/sections/{sec_id}/articles",
                    art_payload
                )
                if not art_result:
                    failed.append(f"Article: {art_data['title']}")
                    continue

                art_id = art_result["article"]["id"]
                art_url = f"{BASE_URL}/hc/{LOCALE}/articles/{art_id}"
                print(f"      ✅ Created article id={art_id}")
                print(f"         URL: {art_url}")
                created["articles"] += 1

                # Update article translation to add description
                desc = art_data.get("description", "")
                if desc:
                    translation_payload = {
                        "translation": {
                            "title": art_data["title"],
                            "body": art_data["body"].strip(),
                            "draft": False
                        }
                    }
                    # Use the update translation endpoint
                    r = requests.put(
                        f"{BASE_URL}/api/v2/help_center/articles/{art_id}/translations/{LOCALE}",
                        auth=AUTH,
                        headers=HEADERS,
                        json=translation_payload,
                        verify=False
                    )
                    if r.status_code in (200, 201):
                        print(f"      ✅ Description set")
                    else:
                        print(f"      ⚠️  Description update skipped ({r.status_code})")

                sleep(0.5)  # Rate limit protection

    # ── Summary ────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"SEEDING COMPLETE")
    print(f"{'='*60}")
    print(f"  ✅ Categories created: {created['categories']}")
    print(f"  ✅ Sections created:   {created['sections']}")
    print(f"  ✅ Articles created:   {created['articles']}")

    if failed:
        print(f"\n  ❌ Failed items ({len(failed)}):")
        for f_item in failed:
            print(f"     - {f_item}")
    else:
        print(f"\n  🎉 All items created successfully!")

    print(f"\n  View your Help Center:")
    print(f"  {BASE_URL}/hc/{LOCALE}")
    print(f"\n  View Knowledge Admin:")
    print(f"  {BASE_URL}/hc/admin")


if __name__ == "__main__":
    run()
