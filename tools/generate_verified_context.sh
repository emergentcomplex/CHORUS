#!/bin/bash
#
# 🔱 CHORUS Verified Context Generator (v1.0)
#
# This script generates a single, definitive context file for bootstrapping
# an AI development session. It captures the complete, verifiable state of the
# repository, including directory structure and all relevant file contents,
# ensuring perfect state synchronization.

set -e

# --- Configuration ---
OUTPUT_FILE="VERIFIED_CONTEXT.txt"
EXCLUDE_PATTERNS=(
    -path "./.git/*" \
    -path "./venv/*" \
    -path "./data/*" \
    -path "./models/*" \
    -path "./__pycache__/*" \
    -name "*.pyc" \
    -name "*.md" \
    -name "*.sql" \
    -name "*.bak" \
    -name "*CONTEXT*.txt"
)

echo "[*] Generating verified ground-truth context for CHORUS..."

# --- Header ---
echo "# 🔱 CHORUS Verifiable Codebase Context" > "$OUTPUT_FILE"
echo "# Generated on: $(date)" >> "$OUTPUT_FILE"
echo "# This context represents the complete ground truth of the repository." >> "$OUTPUT_FILE"

# --- Part 1: Directory Structure ---
echo -e "\n\n--- PART 1: DIRECTORY STRUCTURE ---\n" >> "$OUTPUT_FILE"
tree -I 'venv|.git|data|models|__pycache__|*.pyc|*.md|*.sql|*CONTEXT*.txt' >> "$OUTPUT_FILE"

# --- Part 2: File Contents ---
echo -e "\n\n--- PART 2: FILE CONTENTS ---\n" >> "$OUTPUT_FILE"

# Use find with -print0 and a while loop to handle all filenames safely.
# The find command constructs an array of arguments for the exclusion patterns.
find . -type f \( "${EXCLUDE_PATTERNS[@]}" \) -prune -o -print0 | while IFS= read -r -d $'\0' file; do
    if [ -f "$file" ]; then
        echo "--- Filename: ${file} ---" >> "$OUTPUT_FILE"
        cat "${file}" >> "$OUTPUT_FILE"
        echo "" >> "$OUTPUT_FILE" # Add a newline for readability between files
    fi
done

echo "[✅] SUCCESS: Complete verified context generated in '$OUTPUT_FILE'."
echo "[*] The ground truth of your repository has been captured."