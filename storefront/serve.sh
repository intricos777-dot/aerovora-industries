#!/usr/bin/env bash
# Serve Aerovora storefront locally for preview
# URL: http://localhost:8080

cd "$(dirname "$0")/../storefront"

echo "=== Aerovora Storefront — Local Preview ==="
echo "URL: http://localhost:8080"
echo "Press Ctrl+C to stop"
echo ""

python3 -m http.server 8080
