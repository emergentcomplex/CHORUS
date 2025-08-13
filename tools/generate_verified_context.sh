#!/bin/bash
#
# 🔱 CHORUS Verified Context Generator (v6.0 - The Standard Input Mandate)
#
# This script generates a single, definitive context file of the codebase.
# It now reads a list of files to exclude from standard input, which is a
# more robust method for preventing content duplication.

set -e

# Change to the directory containing the script, then go up one level.
cd "$(dirname "$0")/.."

# --- Use a temporary file for output ---
OUTPUT_FILE=$(mktemp)

# --- Base exclusion patterns ---
FIND_EXCLUDE_PATTERNS=(
    -path './.git' -o \
    -path './.venv' -o \
    -path './.pytest_cache' -o \
    -path './__pycache__' -o \
    -path './tests/e2e/__pycache__' -o \
    -path './documentation' -o \
    -path './chorus.egg-info' -o \
    -path './docs_build' -o \
    -path './datalake' -o \
    -path './logs' -o \
    -path './models' -o \
    -path './.secrets' -o \
    -name '.env.*' -o \
    -name '.python-version' -o \
    -name 'LICENSE' -o \
    -name '*.log' -o \
    -name '*.sql' -o \
    -name '.env' -o \
    -name '*.pyc' -o \
    -name '*.json' -o \
    -name 'uv.lock'
)

# --- Dynamically add exclusions by reading from standard input ---
while IFS= read -r file_to_exclude; do
    if [ -n "$file_to_exclude" ]; then
        FIND_EXCLUDE_PATTERNS+=(-o -path "./$file_to_exclude")
    fi
done

# --- Header ---
echo "# 🔱 CHORUS Verifiable Codebase Context" > "$OUTPUT_FILE"
echo "# Generated on: $(date)" >> "$OUTPUT_FILE"
echo "# This context represents the complete ground truth of the repository's source code." >> "$OUTPUT_FILE"

# --- Part 1: Directory Structure ---
echo -e "\n\n--- PART 1: DIRECTORY STRUCTURE ---\n" >> "$OUTPUT_FILE"
TREE_EXCLUDE_PATTERN=$(echo "${FIND_EXCLUDE_PATTERNS[@]}" | sed "s/-path '\.\///g" | sed "s/' -o /|/g" | sed "s/'//g" | sed "s/ //g")
tree -I "$TREE_EXCLUDE_PATTERN" >> "$OUTPUT_FILE"

# --- Part 2: File Contents ---
echo -e "\n\n--- PART 2: FILE CONTENTS ---\n" >> "$OUTPUT_FILE"
find . \( "${FIND_EXCLUDE_PATTERNS[@]}" \) -prune -o -type f -print0 | while IFS= read -r -d $'\0' file; do
    if [ -f "$file" ]; then
        echo "--- Filename: ${file} ---" >> "$OUTPUT_FILE"
        python3 tools/refine_context.py "${file}" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE"
    fi
done

# --- Final Step: Output the name of the temporary file ---
echo "$OUTPUT_FILE"