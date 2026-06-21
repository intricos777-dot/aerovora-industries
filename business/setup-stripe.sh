#!/usr/bin/env bash
# Stripe Product & Price Setup Script for Aerovora Industries
# Requires: stripe CLI (npm install -g stripe) and STRIPE_API_KEY set
#
# Usage: STRIPE_API_KEY=sk_live_xxx bash setup-stripe.sh

set -euo pipefail

if [ -z "${STRIPE_API_KEY:-}" ]; then
  echo "ERROR: Set STRIPE_API_KEY (e.g. export STRIPE_API_KEY=sk_live_xxx)"
  echo "Get your key from https://dashboard.stripe.com/apikeys"
  exit 1
fi

if ! command -v stripe &>/dev/null; then
  echo "Installing Stripe CLI..."
  npm install -g stripe 2>/dev/null || {
    echo "Please install: npm install -g stripe"
    exit 1
  }
fi

STRIPE="stripe --api-key $STRIPE_API_KEY"

echo "=== Creating Aerovora Products & Prices ==="

create_product() {
  local name="$1" desc="$2"
  $STRIPE products create \
    --name="$name" \
    --description="$desc" \
    --shippable=true \
    --statement-descriptor="AEROVORA" \
    2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['id'])"
}

create_price() {
  local product_id="$1" amount="$2" currency="usd"
  $STRIPE prices create \
    --product="$product_id" \
    --unit-amount="$amount" \
    --currency="$currency" \
    2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['id'])"
}

create_subscription_price() {
  local product_id="$1" amount="$2" interval="$3" currency="usd"
  $STRIPE prices create \
    --product="$product_id" \
    --unit-amount="$amount" \
    --currency="$currency" \
    --recurring[interval]="$interval" \
    2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['id'])"
}

# --- Drones (one-time) ---
echo "  Scout Drone..."
P1=$(create_product "AV-1 Apis Scout Drone" "Hexacopter with hyperspectral camera + plant health monitoring")
create_price "$P1" 1200000

echo "  Pollinator Drone..."
P2=$(create_product "AV-1 Apis Pollinator Drone" "Hexacopter with pollination wand + micro-sprayer + camera")
create_price "$P2" 2400000

echo "  Complete Drone..."
P3=$(create_product "AV-1 Apis Complete Drone" "Hexacopter with all 5 payload modules")
create_price "$P3" 4500000

# --- DaaS Subscriptions ---
echo "  DaaS Scout..."
P4=$(create_product "DaaS — Scout Tier" "1 drone, business hours support, basic telemetry")
create_subscription_price "$P4" 80000 "month"

echo "  DaaS Grower..."
P5=$(create_product "DaaS — Grower Tier" "3 drones, 24/7 AI support, full analytics, battery swap station")
create_subscription_price "$P5" 180000 "month"

echo "  DaaS Swarm..."
P6=$(create_product "DaaS — Swarm Tier" "10+ drones, 24/7 AI + field service, all data + API, 24h replacement")
create_subscription_price "$P6" 250000 "month"

# --- Accessories ---
echo "  Accessories..."
P7=$(create_product "AV-1 Spare Battery (6S 22,000mAh)" "Replacement battery")
create_price "$P7" 85000

P8=$(create_product "AV-1 Fast Charge Station (4-bay)" "Rapid charging station")
create_price "$P8" 320000

P9=$(create_product "AV-1 Solar Charging Array" "Solar-powered charging")
create_price "$P9" 1200000

P10=$(create_product "AV-1 Transport Case" "Fits 1 drone + 4 payload modules")
create_price "$P10" 120000

P11=$(create_product "AV-1 Battery Swap Station" "Autonomous battery swapping station")
create_price "$P11" 1800000

# --- Service Plans ---
echo "  Service Plans..."
P12=$(create_product "AV-1 Extended Warranty (1 Year)" "Extended warranty + support")
create_price "$P12" 150000

P13=$(create_product "AV-1 Extended Warranty (3 Year)" "Extended warranty + support")
create_price "$P13" 360000

P14=$(create_product "AV-1 On-Site Training (2 Days)" "On-site training")
create_price "$P14" 400000

P15=$(create_product "AV-1 Analytics Subscription" "Per-drone monthly analytics")
create_subscription_price "$P15" 50000 "month"

echo ""
echo "=== All products and prices created successfully ==="
echo ""
echo "Next: Run 'python3 create-payment-links.py' to generate checkout links"
echo "Or create them manually at: https://dashboard.stripe.com/products"
