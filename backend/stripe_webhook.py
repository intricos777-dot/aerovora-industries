#!/usr/bin/env python3
"""
Stripe webhook receiver — runs as a sidecar to forward Stripe events
to the local API.  Use `stripe listen --forward-to http://127.0.0.1:8777/webhook/stripe`
after authenticating with `stripe login`.
"""
import json
import os
import sys
import subprocess
import time

API_URL = "http://127.0.0.1:8777/webhook/stripe"
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

def main():
    print("Aerovora — Stripe Webhook Forwarder")
    print("=" * 50)
    print("Make sure Stripe CLI is installed and authenticated.")
    print()
    print("  stripe login")
    print(f"  stripe listen --forward-to {API_URL}")
    print()
    print("Or use the Stripe Dashboard to configure a webhook endpoint:")
    print("  URL:     https://YOUR-SERVER:8777/webhook/stripe")
    print("  Events:  checkout.session.completed, payment_intent.succeeded")
    print()
    print("For local testing, create orders manually:")
    print(f"  curl -X POST http://127.0.0.1:8777/api/test-order \\")
    print(f"    -H 'Content-Type: application/json' \\")
    print(f"    -d '{json.dumps(TEST_ORDER)}'")
    print()

TEST_ORDER = {
    "customer_email": "test@example.com",
    "customer_name": "Test Farmer",
    "sku": "AV1-S",
    "product_name": "AV-1 Apis Scout Drone",
    "amount_cents": 1200000,
    "currency": "usd",
}

if __name__ == "__main__":
    main()
