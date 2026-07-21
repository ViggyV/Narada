#!/bin/bash
# Installs the Narada Daily Briefing into your existing repo and commits it.
# Usage: unzip narada-briefing.zip && cd narada && ./install.sh
set -euo pipefail
REPO="/Users/vigneshvasan/dev/Narada"
SRC="$(cd "$(dirname "$0")" && pwd)"

[ -d "$REPO/.git" ] || { echo "Error: $REPO is not a git repo"; exit 1; }

mkdir -p "$REPO/.github/workflows"
cp -R "$SRC/ai-daily-briefing" "$REPO/"
cp "$SRC/.github/workflows/daily-briefing.yml" "$REPO/.github/workflows/"

cd "$REPO"
git add ai-daily-briefing .github/workflows/daily-briefing.yml
git commit -m "Add daily 6 AM AI briefing pipeline with blog site"
echo
echo "Installed and committed. Preview the blog now:"
echo "  open $REPO/ai-daily-briefing/site/index.html"
echo "Then: git push, add ANTHROPIC_API_KEY secret, and set Pages source to 'GitHub Actions'."
