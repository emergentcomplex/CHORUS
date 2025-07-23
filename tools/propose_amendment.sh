#!/bin/bash
#
# 🔱 CHORUS Amendment Proposal Tool
#
# This script automates the creation of a formal Amendment Proposal
# by opening a pre-filled new issue in the project's GitHub repository.

# Fetch the repository URL from the git config
REPO_URL=$(git config --get remote.origin.url | sed 's/git@github.com:/https://github.com\//' | sed 's/\.git$//')

if [ -z "$REPO_URL" ]; then
  echo "[!] Could not determine the GitHub repository URL."
  exit 1
fi

# The Amendment Proposal template, URL-encoded
TEMPLATE=$(cat <<'EOF'
---
**Amendment Proposal: [A short, descriptive title for the change]**

**1. The "Why" (The Problem):**
(A clear, concise description of the problem being solved or the capability being added. Why is this change necessary?)

**2. The "What" (The Proposed Change):**
(A high-level description of the proposed architectural change. How does this modify the system as described in the blueprint?)

**3. The Blueprint Impact:**
(A list of the specific sections of `/docs/01_CONSTITUTION.md` that will need to be updated to reflect this change.)
---
EOF
)

# URL-encode the template body
BODY_ENCODED=$(printf %s "$TEMPLATE" | jq -s -R -r @uri)

# The final URL for creating a new issue
NEW_ISSUE_URL="$REPO_URL/issues/new?title=Amendment%20Proposal:%20&body=$BODY_ENCODED&labels=amendment-proposal"

echo "[*] Opening your browser to create a new Amendment Proposal..."
echo "[*] URL: $NEW_ISSUE_URL"

# Open the URL in the default browser
xdg-open "$NEW_ISSUE_URL" 2>/dev/null || open "$NEW_ISSUE_URL" 2>/dev/null || echo "Please open the URL above in your browser."
