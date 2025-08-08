#!/bin/bash
#
# 🔱 CHORUS Verified Context Generator (v3.0 - The Signal Purity Mandate)
#
# This script generates a single, definitive context file of the codebase.
# It is designed to be called by the main `generate_context.sh` script.

set -e

# Change to the directory containing the script, then go up one level.
cd "$(dirname "$0")/.."

# --- Definitive Fix: Use a temporary file for output ---
OUTPUT_FILE=$(mktemp)

# --- THE DEFINITIVE FIX: Refined and explicit exclusion patterns ---
# This list is designed to capture ONLY the essential source code and
# configuration, and to exclude all high-level documentation (handled by the
# main script) and irrelevant artifacts.
FIND_EXCLUDE_PATTERNS=(
    # Version control and local environment
    -path './.git' -o \
    -path './.venv' -o \
    -path './.pytest_cache' -o \
    -path './__pycache__' -o \
    -path './tests/e2e/__pycache__' -o \
    # High-level documentation (handled by the main script)
    -path './docs' -o \
    -path './documentation' -o \
    # Build artifacts and caches
    -path './chorus.egg-info' -o \
    -path './docs_build' -o \
    # Runtime data and logs (not part of the core logic)
    -path './datalake' -o \
    -path './logs' -o \
    -path './models' -o \
    # Specific non-essential files
    -name '.python-version' -o \
    -name 'LICENSE' -o \
    -name '*.log' -o \
    -name '*.md' -o \
    -name '*.sql' -o \
    -name '.env' -o \
    -name '*.pyc' -o \
    -name '*.json' -o \
    -name 'uv.lock' \
)

# --- Header ---
echo "# 🔱 CHORUS Verifiable Codebase Context" > "$OUTPUT_FILE"
echo "# Generated on: $(date)" >> "$OUTPUT_FILE"
echo "# This context represents the complete ground truth of the repository's source code." >> "$OUTPUT_FILE"

# --- Part 1: Directory Structure ---
echo -e "\n\n--- PART 1: DIRECTORY STRUCTURE ---\n" >> "$OUTPUT_FILE"
# Exclude the same patterns from the tree view for consistency.
TREE_EXCLUDE_PATTERN=$(echo "${FIND_EXCLUDE_PATTERNS[@]}" | sed "s/-path '\.\///g" | sed "s/' -o /|/g" | sed "s/'//g" | sed "s/ //g")
tree -I "$TREE_EXCLUDE_PATTERN" >> "$OUTPUT_FILE"

# --- Part 2: File Contents ---
echo -e "\n\n--- PART 2: FILE CONTENTS ---\n" >> "$OUTPUT_FILE"

find . \( "${FIND_EXCLUDE_PATTERNS[@]}" \) -prune -o -type f -print0 | while IFS= read -r -d $'\0' file; do
    if [ -f "$file" ]; then
        echo "--- Filename: ${file} ---" >> "$OUTPUT_FILE"
        cat "${file}" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi
done

# --- Final Step: Output the name of the temporary file ---
# The calling script will use this path to read the content.
echo "$OUTPUT_FILE"