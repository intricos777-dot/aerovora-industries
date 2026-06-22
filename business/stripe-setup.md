# Stripe Setup Guide — Aerovora Industries

## Step 1: Create a Stripe Account

1. Go to **https://stripe.com**
2. Sign up (email: intricos777@gmail.com)
3. Verify email and complete onboarding

## Step 2: Get Your API Keys

1. In Stripe Dashboard, go to **Developers > API Keys**
2. Copy your **Publishable Key** (starts with `pk_live_` or `pk_test_`)

## Step 3: Create Products

Go to **Products > Add Product** and create these:

| Name | Type | Price | Description |
|------|------|-------|-------------|
| AV-1 Apis Scout Drone | One-time | $12,000 | Hyperspectral crop monitoring drone |
| AV-1 Apis Pollinator Drone | One-time | $24,000 | Pollination + micro-spray drone |
| AV-1 Apis Complete Drone | One-time | $45,000 | All 5 payload modules |
| DaaS Scout | Monthly | $800/mo | 1 drone, basic support |
| DaaS Grower | Monthly | $1,800/mo | 3 drones, full support |
| DaaS Swarm | Monthly | $2,500/mo/drone | 10+ drone fleet |

After creating each product, click the three dots next to the price and **Copy Price ID** (looks like `price_1AbCdEfGhIjKlMnOpQrStUvWx`).

## Step 4: Configure the Storefront

Edit `storefront/index.html` and find the `STRIPE_CONFIG` section. Paste in your values:

```js
const STRIPE_CONFIG = {
    publicKey: "pk_live_...",  // Your publishable key
    prices: {
      scout: "price_...",       // $12,000 product price ID
      pollinator: "price_...",  // $24,000 product price ID
      complete: "price_...",    // $45,000 product price ID
      daas_scout: "price_...",  // $800/mo price ID
      daas_grower: "price_...", // $1,800/mo price ID
      daas_swarm: "price_...",  // $2,500/mo price ID
    }
};
```

## Step 5: Set Up PayPal Payout

In Stripe Dashboard > Settings > **Payout settings**, add your bank account (or connect PayPal via Stripe).

Alternatively, link Stripe to PayPal manually:
1. Go to **Settings > Business Settings** in Stripe
2. Under Payouts, set schedule to **Daily**
3. Your PayPal intricos777@gmail.com receives all funds

## Step 6: Test

1. Run the test script: `bash ~/Projects/aerovora-industries/business/setup-stripe.sh`
2. Click "Order Now" on the storefront to verify Stripe Checkout opens
3. Make a $1 test purchase

## Step 7: Push Updates

```bash
cd ~/Projects/aerovora-industries/storefront
git add index.html
git commit -m "Configure Stripe live keys"
git push
```

The storefront will auto-deploy to GitHub Pages.
