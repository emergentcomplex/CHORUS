#!/bin/bash
#
# 🔱 CHORUS Verified Context Generator (v2.2 - Docs Excluded)
#
# This script generates a single, definitive context file for bootstrapping
# an AI development session. It is self-contained and can be run from any directory.

set -e

# Change to the directory containing the script, then go up one level.
cd "$(dirname "$0")/.."

# --- Definitive Fix: Use a temporary file for output ---
# This prevents the script from excluding its own output file.
OUTPUT_FILE=$(mktemp)

# Define patterns for `tree`'s -I flag
TREE_EXCLUDE_PATTERN='venv|.git|datalake|models|__pycache__|*.pyc|*.md|*.sql|*CONTEXT*.txt|*.log|chorus.egg-info|docs_build'

# Define patterns for the `find` command
FIND_EXCLUDE_PATTERNS=(
    -path './.git' -o \
    -path './.venv' -o \
    -path './chorus_engine/datalake' -o \
    -path './models' -o \
    -path './.pytest_cache' -o \
    -path './__pycache__' -o \
    -path './chorus.egg-info' -o \
    -path './docs_build' -o \
    -name '*.pyc' -o \
    -name '*.md' -o \
    -name '*.sql' -o \
    -name '*.bak' -o \
    -name '*.log' -o \
    -name 'uv.lock' -o \
    -name '.env' -o \
    -name '*.txt' \
)

# --- Header ---
echo "# 🔱 CHORUS Verifiable Codebase Context" > "$OUTPUT_FILE"
echo "# Generated on: $(date)" >> "$OUTPUT_FILE"
echo "# This context represents the complete ground truth of the repository." >> "$OUTPUT_FILE"

# --- Part 1: Directory Structure ---
echo -e "\n\n--- PART 1: DIRECTORY STRUCTURE ---\n" >> "$OUTPUT_FILE"
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
