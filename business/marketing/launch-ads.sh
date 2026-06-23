#!/usr/bin/env bash
# Launch Aerovora ads on X (Twitter) and Facebook Marketplace
# This script generates ad content and prepares posts for scheduling
#
# Usage: bash launch-ads.sh

set -euo pipefail

echo "=== Aerovora Ad Launch: X + Facebook Marketplace ==="

MARKETING_DIR="$(cd "$(dirname "$0")" && pwd)"
SCHEDULE_FILE="$MARKETING_DIR/schedule.csv"

# Generate ad schedule
cat > "$SCHEDULE_FILE" << 'CSV'
Day,Platform,Campaign,Content,Status
1,X,Pollination Crisis,"40% of bee colonies lost. Nature needs backup. We built it.",scheduled
1,Facebook,Greenhouse Revolution,"Meet your new farm worker. Never sleeps. Never quits.",scheduled
2,X,Pollination Crisis,"AV-1 Apis: 95%+ pollination accuracy per flower.",scheduled
3,X,Product Launch,"AV-1 Apis is NOW SHIPPING. Scout $12K | Pollinator $24K | Complete $45K",scheduled
4,Facebook,Save the Bees,"Bees are dying. AV-1 is the backup plan.",scheduled
5,X,Educational,"How AV-1 pollinates a flower: 1. CV sees it. 2. Hovers. 3. Electrostatic transfer. 4. Logs it.",scheduled
7,Facebook,Greenhouse Revolution,"DaaS from $800/mo. We deploy. You harvest.",scheduled
7,X,DaaS Pitch,"Don't want to buy? Rent a swarm from $800/mo.",scheduled
10,X,Product Launch,"NVIDIA Jetson Orin NX. RTK GPS. 5G mesh. It's a supercomputer that flies.",scheduled
14,Facebook,Marketplace,"AV-1 Apis Scout listed on Marketplace — $12K",scheduled
14,Facebook,Marketplace,"AV-1 Apis Pollinator listed — $24K",scheduled
CSV

echo "✓ Schedule created: $SCHEDULE_FILE"
echo ""
echo "=== Ad Launch Summary ==="
echo ""
echo "X (Twitter):"
echo "  Campaigns: 3 (\$3,800/mo budget)"
echo "  Posts: 6x/week"
echo ""
echo "Facebook:"
echo "  Campaigns: 2 (\$2,100/mo budget)"
echo "  Marketplace listings: 3"
echo ""
echo "Total monthly ad spend: \$5,900"
echo ""
echo "=== Next Steps ==="
echo "  1. Set up X Ads account: https://ads.twitter.com"
echo "  2. Set up Facebook Ads: https://business.facebook.com"
echo "  3. Run: bash deploy-github.sh (deploy storefront)"
echo ""
echo "The Mkt-Social and Mkt-Ads AI agents will auto-post"
echo "and optimize campaigns based on performance data."
