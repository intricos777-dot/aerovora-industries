#!/usr/bin/env python3
"""Aerovora Industries — Marketing Execution Console.

Executes the marketing strategies from the campaign plans:
  - Generates X/Twitter posts (ready to copy-paste)
  - Generates Facebook Marketplace listing HTML
  - Sends email outreach campaigns
  - Displays ad schedule

Usage:
  ./execute.py              # Interactive menu
  ./execute.py --all        # Generate everything
  ./execute.py x-posts      # Just X posts
  ./execute.py facebook     # Facebook listings
  ./execute.py email        # Email outreach
"""

import json
import os
import smtplib
import ssl
import subprocess
import sys
import textwrap
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from pathlib import Path

HERE = Path(__file__).parent
PROJECT = HERE.parent.parent
STOREFRONT_URL = "https://intricos777-dot.github.io/aerovora-storefront"
INVESTOR_URL = f"{STOREFRONT_URL}/investor.html"
REPO_URL = "https://github.com/intricos777-dot/aerovora-industries"
CONTACT_EMAIL = "intricos777@gmail.com"


def banner():
    print("=" * 60)
    print("  AEROVORA INDUSTRIES — MARKETING EXECUTION CONSOLE")
    print("=" * 60)


# ── X (Twitter) Posts ──


def generate_x_posts():
    posts = [
        # Campaign 1: Pollination Crisis
        ("Pollination Crisis", """\
40% of bee colonies lost this year.

Almonds, apples, cherries — they all need pollination. Nature needs a backup plan. We built one. 🤖🐝

AV-1 Apis: autonomous pollination with 95%+ per-flower accuracy. No chemicals. No human pilot.

{STOREFRONT_URL}
#agtech #pollination #aerovora"""),

        ("Pollination Crisis", """\
Meet the AV-1 Apis.

Autonomous hexacopter that pollinates flowers with 95%+ accuracy — per flower, not per field.

No chemicals. No human pilot. Just precision.

{STOREFRONT_URL}
#drones #agriculture #AI"""),

        ("Pollination Crisis", """\
35 min flight time · 6 m/s cruise · 5G swarm mesh
98.2% disease detection · 92% less chemicals

The AV-1 isn't a drone. It's a farm worker that never sleeps.

{STOREFRONT_URL}
#precisionagriculture #agtech"""),

        # Campaign 2: Product Launch
        ("Product Launch", """\
AV-1 Apis is NOW SHIPPING.

Three models, one mission:

Scout — $12,000 — Hyperspectral monitoring
Pollinator — $24,000 — Pollination + micro-spray
Complete — $45,000 — All 5 payload modules

Order: {STOREFRONT_URL}
#AV1Apis #AgTech #Drones"""),

        ("Product Launch", """\
Don't want to buy? Rent a swarm.

AV-1 Drone-as-a-Service:
Scout: $800/mo · 1 drone
Grower: $1,800/mo · 3 drones
Swarm: $2,500/mo · 10+ drones

We deploy, maintain, operate. You get the data.

{STOREFRONT_URL}
#DroneasaService #Agriculture"""),

        ("Product Launch", """\
NVIDIA Jetson Orin NX 16GB · 100 TOPS
RTK GPS ±2.5cm · 5G + LoRa mesh
35 min flight · hot-swappable payloads

It's a supercomputer that flies.

{STOREFRONT_URL}
#AI #Robotics #AgTech"""),

        # Campaign 3: Educational
        ("Educational", """\
How the AV-1 Apis pollinates a flower:

1. Computer vision identifies target flower
2. Drone hovers at 15cm with RTK precision
3. Electrostatic wand transfers pollen
4. AI logs flower as "pollinated" with timestamp
5. Repeats 40x per minute

Per-plant agriculture. 🧠🌱"""),

        ("Educational", """\
Inside every AV-1:
• NVIDIA Jetson Orin (100 TOPS)
• Custom CNN for disease detection (98.2%)
• Swarm mesh networking (unlimited scale)
• Autonomous charging + data sync

It's not a drone. It's a flying supercomputer for your crops."""),

        ("Educational", """\
One AV-1 is impressive. 100 AV-1s is a revolution.

Our swarm AI coordinates drones across 1,000+ acres — allocating pollination, monitoring, and spraying in real-time based on plant needs.

Every plant gets exactly what it needs.
{STOREFRONT_URL}"""),

        # Comparison
        ("Educational", """\
Broadcast spraying vs AV-1 micro-spraying:

Broadcast: 100% coverage, <5% hits target
AV-1: 2cm precision, 92% less chemical, 100% targeted

The math is simple.
{STOREFRONT_URL}
#SustainableAgriculture #AgTech"""),
    ]

    print("\n── X (Twitter) Posts ──\n")
    print(f"Ready to post at @AerovoraIndustries")
    print(f"Schedule: 6 posts/week across 3 campaigns\n")

    for i, (campaign, text) in enumerate(posts, 1):
        formatted = text.format(STOREFRONT_URL=STOREFRONT_URL)
        print(f"─── Post #{i} [{campaign}] ───")
        for line in formatted.strip().split("\n"):
            print(f"  {line}")
        print()

    print(f"─── End of X posts ({len(posts)} total) ───\n")
    return posts


# ── Facebook Marketplace ──


def generate_facebook_listings():
    listings = [
        {
            "title": "AV-1 Apis Autonomous Farm Drone — Crop Monitoring & Disease Detection",
            "price": "$12,000",
            "category": "Agriculture & Forestry > Farm Machinery > Drones & UAVs",
            "condition": "New (shipping from manufacturer)",
            "description": textwrap.dedent("""\
            The AV-1 Apis Scout is an AI-powered autonomous hexacopter for precision crop monitoring.

            • Hyperspectral camera (5-band: RGB, NIR, Red-edge, thermal)
            • 98.2% disease detection accuracy across 47 crop types
            • 22 nutrient deficiency patterns identified
            • NVIDIA Jetson Orin NX 16GB onboard AI
            • 35 min flight time, 6 m/s cruise
            • RTK GPS ±2.5cm positioning
            • Fully autonomous — no pilot required
            • 5G + WiFi 6 + LoRa mesh connectivity

            No subscription required. One-time purchase includes drone, charger, and training guide.

            Financing available. DaaS rental options from $800/mo.

            Ships from AeroFab-1 (USA) · 5-10 business days
            Warranty: 1 year included, up to 3 year extended
            """),
            "type": "product",
        },
        {
            "title": "AV-1 Apis Pollinator Drone — Autonomous Pollination + Micro-Spraying",
            "price": "$24,000",
            "category": "Agriculture & Forestry > Farm Machinery > Drones & UAVs",
            "condition": "New",
            "description": textwrap.dedent("""\
            The AV-1 Apis Pollinator replaces manual pollination and broadcast spraying with AI-driven precision.

            • Electrostatic pollination wand — 95%+ per-flower success
            • Micro-sprayer — 2cm precision, 92% less chemicals
            • 500g pollen reservoir + 2L spray tank
            • All Scout features included (hyperspectral, disease detection)
            • NVIDIA Jetson Orin NX 16GB
            • 35 min flight, autonomous charging

            Ideal for: Almonds, apples, cherries, avocados, greenhouse tomatoes, berries.

            Financing available. DaaS from $1,800/mo for 3 drones.
            Ships from AeroFab-1 (USA) · 5-10 business days
            """),
            "type": "product",
        },
        {
            "title": "Rent a Bee Drone Swarm — No Upfront Cost, $800/mo",
            "price": "$800/mo",
            "category": "Agriculture & Forestry > Services",
            "condition": "Service",
            "description": textwrap.dedent("""\
            Get Aerovora's autonomous plant caretaking drones without buying hardware.

            Scout Tier — $800/mo
            • 1 AV-1 Apis drone
            • Business hours AI support
            • Weekly aerial surveys + health reports
            • All software updates included

            Grower Tier — $1,800/mo
            • 3 AV-1 Apis drones
            • 24/7 AI support
            • Battery swap station included
            • Daily reports + analytics dashboard

            Swarm Tier — $2,500/mo per drone (10+)
            • Full fleet + field service
            • Custom payload configurations
            • Dedicated swarm orchestration AI

            No long-term contract required (12mo commitment for best pricing).
            We deploy, maintain, and operate. You get healthier crops.
            """),
            "type": "service",
        },
    ]

    print("── Facebook Marketplace Listings ──\n")
    for i, listing in enumerate(listings, 1):
        print(f"─── Listing #{i} — {listing['title']} ───")
        print(f"  Price: {listing['price']}")
        print(f"  Category: {listing['category']}")
        print(f"  Condition: {listing['condition']}")
        print(f"  Description:")
        for line in listing["description"].strip().split("\n"):
            print(f"    {line.strip()}")
        print()

    print(f"─── End of listings ({len(listings)} total) ───\n")
    return listings


# ── Email Outreach ──


def generate_emails():
    segments = [
        {
            "segment": "Greenhouse Operators",
            "subject": "Your greenhouse needs a farm worker that never sleeps",
            "body": textwrap.dedent("""\
            Hi {{first_name}},

            Greenhouse operations run 24/7, but your workforce doesn't. Meet the AV-1 Apis — an autonomous drone that monitors, pollinates, and treats every plant as an individual.

            What it does for your greenhouse:
            • Patrols 24/7 detecting disease before it spreads (98.2% accuracy)
            • Pollinates flowers with 95%+ per-flower precision
            • Sprays only the plants that need it — 92% less chemical usage
            • Generates per-plant health reports automatically

            No upfront hardware: DaaS from $800/mo per drone. We deploy, maintain, and operate.

            See it in action: {STOREFRONT_URL}

            Reply to schedule a demo.

            — Aerovora Industries
            AI-operated. Precision agriculture.
            """),
        },
        {
            "segment": "Orchard Owners",
            "subject": "40% of bees died this year. Your orchard needs a backup plan.",
            "body": textwrap.dedent("""\
            Hi {{first_name}},

            Bee colony collapse isn't a future problem — it's happening now. Almond orchards alone need 2.4 million hives annually, and there aren't enough.

            The AV-1 Apis Pollinator drone replaces manual pollination with autonomous precision:
            • Electrostatic pollen transfer: 95%+ per-flower success
            • 500g pollen reservoir per flight
            • Works 24/7 in any weather bees can't
            • Also monitors for disease + nutrient deficiency

            Available now: Purchase from $24K per drone, or DaaS from $800/mo.

            {STOREFRONT_URL}

            Your orchard can't wait another season.

            — Aerovora Industries
            """),
        },
        {
            "segment": "Row Crop Farmers",
            "subject": "Stop spraying your whole field. Treat each plant.",
            "body": textwrap.dedent("""\
            Hi {{first_name}},

            Broadcast spraying covers 100% of your field but <5% hits the target. That's 95% waste — chemical, money, and environmental.

            The AV-1 Apis Complete drone targets individual plants with 2cm precision:
            • Micro-sprayer: 50-400μm droplets, computer-vision targeted
            • Hyperspectral imaging: detects disease + deficiency before visible
            • LIDAR scanning: 3D crop modeling for yield forecasting
            • Swarm mode: 100+ drones coordinating across 1,000+ acres

            DaaS from $800/mo/drone. No capital expenditure.

            {STOREFRONT_URL}

            — Aerovora Industries
            """),
        },
        {
            "segment": "Investors",
            "subject": "Investing in the AI-operated future of agriculture",
            "body": textwrap.dedent("""\
            Hi {{first_name}},

            Aerovora Industries is building the world's first fully AI-operated company — an autonomous bee drone manufacturer for precision plant caretaking.

            Key investment highlights:
            • $18.2B agricultural drone market (31.2% CAGR)
            • 35 AI agents + 11 robots operating the entire company
            • 94% decisions autonomous, only 1% need human input
            • Revenue: Y1 $3.2M → Y3 $72M
            • Seed round: $850K

            Product: AV-1 Apis hexacopter with 5 hot-swappable payload modules. NVIDIA Jetson Orin NX onboard.

            Business model: Direct sales ($12K-$45K) + DaaS ($800-$2,500/mo) + data analytics.

            Full company structure (public): {REPO_URL}
            Storefront: {STOREFRONT_URL}
            Investor deck: {INVESTOR_URL}

            I'd love to schedule a call to walk you through the opportunity.

            — Aerovora Industries
            {CONTACT_EMAIL}
            """),
        },
    ]

    print("── Email Outreach Campaigns ──\n")
    for i, s in enumerate(segments, 1):
        body = s["body"].format(
            STOREFRONT_URL=STOREFRONT_URL,
            REPO_URL=REPO_URL,
            INVESTOR_URL=INVESTOR_URL,
            CONTACT_EMAIL=CONTACT_EMAIL,
        )
        print(f"─── Segment #{i}: {s['segment']} ───")
        print(f"  Subject: {s['subject']}")
        print(f"  Body:")
        for line in body.strip().split("\n"):
            print(f"    {line}")
        print()

    print(f"─── End of email segments ({len(segments)} total) ───\n")
    return segments


# ── Send Emails (SMTP) ──


def send_emails():
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "")
    from_email = os.getenv("FROM_EMAIL", smtp_user)

    if not smtp_user or not smtp_pass:
        print("ERROR: SMTP credentials not configured.")
        print("Set SMTP_USER, SMTP_PASS, SMTP_SERVER, SMTP_PORT")
        return

    contacts_file = HERE / "contacts.csv"
    if not contacts_file.exists():
        print("ERROR: Create contacts.csv first:")
        print("  Format: first_name,email,segment")
        print("  Example: John,john@farm.com,Orchard Owners")
        return

    import csv
    with open(contacts_file) as f:
        contacts = list(csv.DictReader(f))

    if not contacts:
        print("No contacts found in contacts.csv")
        return

    segments = generate_emails_plain()
    print(f"Sending {len(contacts)} emails via {smtp_server}:{smtp_port}...")

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls(context=context)
        server.login(smtp_user, smtp_pass)

        for contact in contacts:
            first_name = contact.get("first_name", "Farmer")
            email = contact.get("email", "")
            segment_name = contact.get("segment", "Greenhouse Operators")

            seg = next((s for s in segments if s["segment"] == segment_name), segments[0])
            body = seg["body"].format(
                STOREFRONT_URL=STOREFRONT_URL,
                REPO_URL=REPO_URL,
                INVESTOR_URL=INVESTOR_URL,
                CONTACT_EMAIL=CONTACT_EMAIL,
            ).replace("{{first_name}}", first_name)

            msg = MIMEText(body.strip(), "plain")
            msg["Subject"] = seg["subject"]
            msg["From"] = from_email
            msg["To"] = email

            server.send_message(msg)
            print(f"  ✓ {email} ({first_name}) — {seg['segment']}")

    print(f"\nDone! Sent {len(contacts)} emails.")


def generate_emails_plain():
    return [
        {
            "segment": "Greenhouse Operators",
            "subject": "Your greenhouse needs a farm worker that never sleeps",
            "body": textwrap.dedent("""\
            Hi {{first_name}},

            Greenhouse operations run 24/7, but your workforce doesn't. Meet the AV-1 Apis — an autonomous drone that monitors, pollinates, and treats every plant as an individual.

            What it does for your greenhouse:
            • Patrols 24/7 detecting disease before it spreads (98.2% accuracy)
            • Pollinates flowers with 95%+ per-flower precision
            • Sprays only the plants that need it — 92% less chemical usage
            • Generates per-plant health reports automatically

            No upfront hardware: DaaS from $800/mo per drone. We deploy, maintain, and operate.

            See it in action: {STOREFRONT_URL}

            Reply to schedule a demo.

            — Aerovora Industries
            AI-operated. Precision agriculture.
            """),
        },
        {
            "segment": "Orchard Owners",
            "subject": "40% of bees died this year. Your orchard needs a backup plan.",
            "body": textwrap.dedent("""\
            Hi {{first_name}},

            Bee colony collapse isn't a future problem — it's happening now. Almond orchards alone need 2.4 million hives annually, and there aren't enough.

            The AV-1 Apis Pollinator drone replaces manual pollination with autonomous precision:
            • Electrostatic pollen transfer: 95%+ per-flower success
            • 500g pollen reservoir per flight
            • Works 24/7 in any weather bees can't
            • Also monitors for disease + nutrient deficiency

            Available now: Purchase from $24K per drone, or DaaS from $800/mo.

            {STOREFRONT_URL}

            Your orchard can't wait another season.

            — Aerovora Industries
            """),
        },
        {
            "segment": "Row Crop Farmers",
            "subject": "Stop spraying your whole field. Treat each plant.",
            "body": textwrap.dedent("""\
            Hi {{first_name}},

            Broadcast spraying covers 100% of your field but <5% hits the target. That's 95% waste — chemical, money, and environmental.

            The AV-1 Apis Complete drone targets individual plants with 2cm precision:
            • Micro-sprayer: 50-400μm droplets, computer-vision targeted
            • Hyperspectral imaging: detects disease + deficiency before visible
            • LIDAR scanning: 3D crop modeling for yield forecasting
            • Swarm mode: 100+ drones coordinating across 1,000+ acres

            DaaS from $800/mo/drone. No capital expenditure.

            {STOREFRONT_URL}

            — Aerovora Industries
            """),
        },
        {
            "segment": "Investors",
            "subject": "Investing in the AI-operated future of agriculture",
            "body": textwrap.dedent("""\
            Hi {{first_name}},

            Aerovora Industries is building the world's first fully AI-operated company — an autonomous bee drone manufacturer for precision plant caretaking.

            Key investment highlights:
            • $18.2B agricultural drone market (31.2% CAGR)
            • 35 AI agents + 11 robots operating the entire company
            • 94% decisions autonomous, only 1% need human input
            • Revenue: Y1 $3.2M → Y3 $72M
            • Seed round: $850K

            Product: AV-1 Apis hexacopter with 5 hot-swappable payload modules. NVIDIA Jetson Orin NX onboard.

            Business model: Direct sales ($12K-$45K) + DaaS ($800-$2,500/mo) + data analytics.

            Full company structure (public): {REPO_URL}
            Storefront: {STOREFRONT_URL}
            Investor deck: {INVESTOR_URL}

            I'd love to schedule a call to walk you through the opportunity.

            — Aerovora Industries
            {CONTACT_EMAIL}
            """),
        },
    ]


# ── Main ──


def main():
    actions = {
        "x-posts": generate_x_posts,
        "facebook": generate_facebook_listings,
        "email": generate_emails,
        "send-email": send_emails,
    }

    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--all":
            generate_x_posts()
            generate_facebook_listings()
            generate_emails()
        elif arg in actions:
            actions[arg]()
        else:
            print(f"Unknown action: {arg}")
            print(f"Available: {' '.join(actions.keys())} --all")
            sys.exit(1)
        return

    banner()
    print()
    print("  1) Generate X (Twitter) posts")
    print("  2) Generate Facebook Marketplace listings")
    print("  3) Generate email outreach templates")
    print("  4) Send email campaign (requires SMTP config)")
    print("  5) Generate ALL")
    print("  q) Quit")
    print()

    choice = input("  Select: ").strip()

    if choice == "1":
        generate_x_posts()
    elif choice == "2":
        generate_facebook_listings()
    elif choice == "3":
        generate_emails()
    elif choice == "4":
        send_emails()
    elif choice == "5":
        generate_x_posts()
        generate_facebook_listings()
        generate_emails()
    elif choice.lower() == "q":
        return
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()
