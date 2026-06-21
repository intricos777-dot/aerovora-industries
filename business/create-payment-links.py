#!/usr/bin/env python3
"""Generate Stripe Payment Links for Aerovora product catalog.
Run after setup-stripe.sh populates products & prices.

Usage: python3 create-payment-links.py
"""

import json
import os
import subprocess
import sys

STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "")
if not STRIPE_API_KEY:
    print("ERROR: Set STRIPE_API_KEY environment variable")
    sys.exit(1)

def run_stripe(*args):
    cmd = ["stripe", "--api-key", STRIPE_API_KEY] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None
    return json.loads(result.stdout) if result.stdout else {}

def list_prices():
    """Get all active prices from Stripe."""
    data = run_stripe("prices", "list", "--limit=100")
    if data:
        return data.get("data", [])
    return []

def create_payment_link(price_id, quantity=1):
    """Create a payment link for a given price."""
    data = run_stripe(
        "payment_links", "create",
        f"--line-items=[{{\"price\":\"{price_id}\",\"quantity\":{quantity}}}]",
        "--after-completion=redirect",
        "--allow-promotion-codes=true"
    )
    return data.get("url", "") if data else ""

def main():
    prices = list_prices()
    if not prices:
        print("No prices found. Run setup-stripe.sh first.")
        sys.exit(1)

    print(f"Found {len(prices)} prices. Creating payment links...\n")

    payment_links = []
    for price in prices:
        product = price.get("product", "unknown")
        unit_amount = price.get("unit_amount", 0)
        currency = price.get("currency", "usd")
        recurring = price.get("recurring", None)

        name = "Unknown"
        if isinstance(product, str) and product.startswith("prod_"):
            product_data = run_stripe("products", "retrieve", product)
            if product_data:
                name = product_data.get("name", "Unknown")

        price_type = "subscription" if recurring else "one-time"
        url = create_payment_link(price["id"])

        link_data = {
            "product": name,
            "type": price_type,
            "price": f"${unit_amount/100:.2f}/mo" if recurring else f"${unit_amount/100:.2f}",
            "payment_link": url,
        }
        payment_links.append(link_data)

        status = "✓" if url else "✗"
        price_str = f"${unit_amount/100:.2f}/mo" if recurring else f"${unit_amount/100:.2f}"
        print(f"  {status} {name}: {price_str} → {url or 'FAILED'}")

    # Save to JSON
    output_path = os.path.join(os.path.dirname(__file__), "payment-links.json")
    with open(output_path, "w") as f:
        json.dump(payment_links, f, indent=2)
    print(f"\nSaved to {output_path}")

if __name__ == "__main__":
    main()
