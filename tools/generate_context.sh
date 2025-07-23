#!/bin/bash
#
# 🔱 CHORUS Genesis Context Generator (v2.0)
#
# Gathers all necessary context from the definitive /docs directory.

cd "$(dirname "$0")/.."
OUTPUT_FILE="CONTEXT_FOR_AI.txt"

echo "[*] Generating Genesis context for CHORUS..."

# 1. Start with the Genesis Prompt itself.
cat docs/GENESIS_PROMPT.md > $OUTPUT_FILE
echo -e "\n\n---\n" >> $OUTPUT_FILE

# 2. Append the Logos (The Constitution)
echo "--- PART 1: THE LOGOS (The Constitution) ---" >> $OUTPUT_FILE
cat docs/01_CONSTITUTION.md >> $OUTPUT_FILE
echo -e "\n\n---\n" >> $OUTPUT_FILE

# 3. Append the Ethos (The Mission & Contribution Guide)
echo "--- PART 2: THE ETHOS (The Law) ---" >> $OUTPUT_FILE
cat docs/00_MISSION_CHARTER.md >> $OUTPUT_FILE
echo -e "\n\n" >> $OUTPUT_FILE
cat docs/02_CONTRIBUTING.md >> $OUTPUT_FILE
echo -e "\n\n---\n" >> $OUTPUT_FILE

# 4. Append the Land (The Codebase Structure)
echo "--- PART 3: THE LAND (The Codebase) ---" >> $OUTPUT_FILE
ls -R >> $OUTPUT_FILE

echo "[+] SUCCESS: Complete context generated in '$OUTPUT_FILE'"