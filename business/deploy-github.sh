#!/usr/bin/env bash
# Deploy Aerovora storefront to GitHub Pages
#
# Prerequisites:
#   1. Create a GitHub repo: gh repo create aerovora-storefront --public
#   2. Run this script
#
# Usage: bash deploy-github.sh

set -euo pipefail

echo "=== Aerovora Storefront — GitHub Pages Deploy ==="

# Configuration
REPO_NAME="aerovora-storefront"
BRANCH="gh-pages"
SOURCE_DIR="/root/Projects/aerovora-industries/storefront"

# Check for GitHub CLI
if ! command -v gh &>/dev/null; then
  echo "Installing GitHub CLI..."
  pacman -S --noconfirm github-cli 2>/dev/null || {
    echo "Please install gh: https://cli.github.com/"
    echo "Or manually: create a repo and push the storefront/ folder to gh-pages branch"
    exit 1
  }
fi

# Check auth
if ! gh auth status &>/dev/null; then
  echo "Please login to GitHub first:"
  echo "  gh auth login"
  exit 1
fi

echo "Creating repository..."
gh repo create "$REPO_NAME" --public --description "Aerovora Industries — Autonomous Bee Drones for Plant Caretaking" --homepage "https://$(gh api user -q .login).github.io/$REPO_NAME" 2>/dev/null || true

echo "Deploying storefront to $BRANCH branch..."
cd "$SOURCE_DIR"

# Init git if needed
if [ ! -d .git ]; then
  git init
  git checkout -b "$BRANCH"
fi

git add -A
git commit -m "Deploy storefront $(date +%Y-%m-%d)" 2>/dev/null || echo "Nothing to commit"

git remote add origin "https://github.com/$(gh api user -q .login)/$REPO_NAME.git" 2>/dev/null || true
git push -f origin "$BRANCH"

echo ""
echo "=== Deployed! ==="
echo "URL: https://$(gh api user -q .login).github.io/$REPO_NAME"
echo ""
echo "Next steps:"
echo "  1. Enable GitHub Pages in repo Settings > Pages (source: gh-pages)"
echo "  2. Set up custom domain (aerovora.com) if desired"
echo "  3. Connect Stripe for payments"
