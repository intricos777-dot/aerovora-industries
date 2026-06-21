# Aerovora Industries — Payment & Revenue Routing

## Primary Payout Account

| Field | Value |
|-------|-------|
| **Platform** | PayPal |
| **Email** | intricos777@gmail.com |
| **Type** | Personal/Business |
| **Currency** | USD |
| **Routing Priority** | Primary (100% of proceeds) |

---

## Revenue Sources & Payout Flow

```
[Revenue Source]                → [Processor]           → [Payout Destination]
──────────────────────────────────────────────────────────────────────────────
Drone Sales (AV1-S, AV1-P, AV1-C) → Stripe             → PayPal intricos777@gmail.com
Drone-as-a-Service subscriptions  → Stripe (recurring)  → PayPal intricos777@gmail.com
Data analytics subscriptions      → Stripe (recurring)  → PayPal intricos777@gmail.com
Parts & accessories sales         → Stripe             → PayPal intricos777@gmail.com
Enterprise contracts (net-30)     → Stripe invoices    → PayPal intricos777@gmail.com
```

---

## Payment Processor Configuration

### Stripe
- Payout schedule: Daily (automatic)
- Payout method: Standard (bank → PayPal transfer)
- Statement descriptor: `AEROVORA*`
- Webhook events: `payment_intent.succeeded`, `invoice.paid`, `subscription.created`

### PayPal Business Account
- Email: intricos777@gmail.com
- Payout currency: USD
- Withdrawal: Manual or auto-sweep to linked bank (as configured by account owner)

---

## Commission / Fee Structure

| Fee Type | Rate | Paid By |
|----------|------|---------|
| Stripe processing | 2.9% + $0.30 | Aerovora (deducted before payout) |
| PayPal withdrawal | Free (standard) | Aerovora |
| Cross-border fee | +1.5% if applicable | Aerovora |

---

## Auto-Routing Configuration

Configured in the Finance AI agent (Strat-Fin):

```json
{
  "revenue_routing": {
    "primary_destination": {
      "type": "paypal",
      "identifier": "intricos777@gmail.com",
      "allocation_pct": 100
    },
    "reserve_account": {
      "type": "paypal",
      "identifier": "intricos777@gmail.com",
      "allocation_pct": 0
    },
    "payout_schedule": "auto_daily",
    "min_payout_threshold_usd": 1.00
  }
}
```

---

## Integration Setup Checklist

- [ ] Create Stripe account (if not existing)
- [ ] Configure Stripe → PayPal payout bridge
- [ ] Set PayPal email intricos777@gmail.com as primary payout destination
- [ ] Configure webhook endpoints in Stripe dashboard
- [ ] Test payment flow with $1.00 transaction
- [ ] Verify payout arrives in PayPal account
- [ ] Enable automatic daily payouts
- [ ] Set up Stripe Tax for automated sales tax collection
- [ ] Configure recurring billing for DaaS subscriptions
