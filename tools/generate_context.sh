#!/bin/bash
#
# 🔱 CHORUS Re-Genesis Context Generator (v24 - The Mandate of Praxis Integrity)
#
# This script guarantees a duplication-free context and ensures the Praxis
# section is always populated. It uses a stateful, single-pass approach and
# adds explicit validation for the mission-critical Praxis file.

set -e

# --- Configuration ---
OUTPUT_FILE="CONTEXT_FOR_AI.txt"
PROCESSED_FILES_LOG=$(mktemp)
trap 'rm -f "$PROCESSED_FILES_LOG"' EXIT

# --- Step 1: Argument and Path Validation ---
cd "$(dirname "$0")/.." # Navigate to project root

PRAXIS_FILE=$1
if [ -z "$PRAXIS_FILE" ] || [ ! -f "$PRAXIS_FILE" ]; then
    echo "[!] FATAL ERROR: You must provide a valid path to a mission brief."
    echo "    Usage: $0 docs/missions/some_mandate.md"
    exit 1
fi

# THE DEFINITIVE FIX: Add an explicit check to ensure the Praxis file has content.
if [ ! -s "$PRAXIS_FILE" ]; then
    echo "[!] FATAL ERROR: The provided Praxis file is empty or does not exist."
    echo "    File path: $PRAXIS_FILE"
    exit 1
fi

echo "[*] Generating context with the Praxis Integrity protocol..."
echo "[*] Using mission brief: $PRAXIS_FILE"

# --- Step 2: Define the static header files (Praxis is now handled separately) ---
HEADER_FILES=(
    "docs/00_THE_CONSTITUTION.md"
    "docs/04_THE_VERIFICATION_COVENANT.md"
    "docs/01_THE_MISSION.md"
    "docs/05_THE_CONTRIBUTING_GUIDE.md"
    "docs/03_THE_SYSTEM_SLOS.md"
)

# --- Step 3: Write the Preamble and the Header ---
# This section writes the header content and simultaneously logs the files
# to our temporary tracking file.

# Write Preamble
cat > "$OUTPUT_FILE" << 'PREAMBLE'
# 🔱 CHORUS Re-Genesis Prompt

You are a core developer for **CHORUS**. Your task is to execute the Master Plan provided in the Praxis section below, guided by the Constitution and Ethos. The final section, The Land, is the complete ground truth of the codebase.
PREAMBLE

# Write Header Parts and log them as processed
{
    echo -e "\n\n---\n### **PART 1: THE LOGOS (The Constitution)**"
    cat "${HEADER_FILES[0]}"
    echo "./${HEADER_FILES[0]}" >> "$PROCESSED_FILES_LOG"

    echo -e "\n\n---\n### **PART 2: THE VERIFICATION COVENANT**"
    cat "${HEADER_FILES[1]}"
    echo "./${HEADER_FILES[1]}" >> "$PROCESSED_FILES_LOG"

    # THE DEFINITIVE FIX: Explicitly handle the Praxis file.
    echo -e "\n\n---\n### **PART 3: THE PRAXIS (The Master Plan)**"
    cat "$PRAXIS_FILE"
    echo "./$PRAXIS_FILE" >> "$PROCESSED_FILES_LOG"

    echo -e "\n\n---\n### **PART 4: THE ETHOS (The Mission & Rules)**"
    cat "${HEADER_FILES[2]}"
    echo "./${HEADER_FILES[2]}" >> "$PROCESSED_FILES_LOG"
    echo -e "\n\n"
    cat "${HEADER_FILES[3]}"
    echo "./${HEADER_FILES[3]}" >> "$PROCESSED_FILES_LOG"
    echo -e "\n\n"
    cat "${HEADER_FILES[4]}"
    echo "./${HEADER_FILES[4]}" >> "$PROCESSED_FILES_LOG"

    echo -e "\n\n---\n### **PART 5: THE LAND (The Codebase)**"
} >> "$OUTPUT_FILE"

# --- Step 4: Write The Land, excluding all previously processed files ---
# This section uses the existing, correct exclusion logic.

EXCLUDE_PATTERNS=(
    -path './.git' -o \
    -path './.venv' -o \
    -path './.pytest_cache' -o \
    -path './__pycache__' -o \
    -path './chorus.egg-info' -o \
    -path './docs_build' -o \
    -path './datalake' -o \
    -path './logs' -o \
    -path './models' -o \
    -path './documentation' -o \
    -path './kafka_connect.log' -o \
    -path './stream_processor.log' -o \
    -name 'CONTEXT_FOR_AI.txt' -o \
    -name '*.pyc' -o \
    -name '*.json' -o \
    -name '.secrets' -o \
    -name 'uv.lock'
)
# Log the script itself to prevent it from being included in the context
echo "./tools/generate_context.sh" >> "$PROCESSED_FILES_LOG"

# --- Generate Directory Structure ---
echo -e "\n\n--- DIRECTORY STRUCTURE ---\n" >> "$OUTPUT_FILE"
tree_exclusions=()
i=0
while [ $i -lt ${#EXCLUDE_PATTERNS[@]} ]; do
    current_element="${EXCLUDE_PATTERNS[i]}"
    if [[ "$current_element" == "-path" || "$current_element" == "-name" ]]; then
        path_value="${EXCLUDE_PATTERNS[i+1]}"
        cleaned_path="${path_value#./}"
        tree_exclusions+=("$cleaned_path")
        i=$((i + 2))
    else
        i=$((i + 1))
    fi
done
while IFS= read -r line; do
    tree_exclusions+=("${line#./}")
done < "$PROCESSED_FILES_LOG"
TREE_EXCLUDE_PATTERN=$(IFS='|'; echo "${tree_exclusions[*]}")
tree -I "$TREE_EXCLUDE_PATTERN" >> "$OUTPUT_FILE"

# --- Generate File Contents ---
echo -e "\n\n--- FILE CONTENTS ---\n" >> "$OUTPUT_FILE"
find . \( "${EXCLUDE_PATTERNS[@]}" \) -prune -o -type f -print0 | \
    grep -vFzZf "$PROCESSED_FILES_LOG" | \
    while IFS= read -r -d $'\0' file; do
        if [ -f "$file" ]; then
            echo "--- Filename: ${file} ---" >> "$OUTPUT_FILE"
            if [[ "$file" == *.py ]]; then
                python3 tools/refine_context.py "${file}" >> "$OUTPUT_FILE"
            else
                cat "${file}" >> "$OUTPUT_FILE"
            fi
            echo "" >> "$OUTPUT_FILE"
        fi
    done

echo "[+] SUCCESS: Context generated with guaranteed Praxis integrity. Output is in '$OUTPUT_FILE'"