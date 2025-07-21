#!/bin/bash
#
# 🔱 CHORUS Genesis Context Generator
#
# This script gathers all necessary context from the repository into a single
# file, ready to be pasted into a new LLM conversation to bootstrap the
# development process with perfect, version-controlled context.

# Navigate to the project root from the script's location
cd "$(dirname "$0")/.."

# Define the output file (it will be ignored by .gitignore)
OUTPUT_FILE="CONTEXT_FOR_AI.txt"

echo "[*] Generating Genesis context for CHORUS..."

# 1. Start with the Genesis Prompt itself.
cat docs/GENESIS_PROMPT.md > $OUTPUT_FILE
echo -e "\n\n---\n" >> $OUTPUT_FILE

# 2. Append the Logos (The Blueprint)
echo "--- PART 1: THE LOGOS (The Constitution) ---" >> $OUTPUT_FILE
cat docs/blueprint.md >> $OUTPUT_FILE
echo -e "\n\n---\n" >> $OUTPUT_FILE

# 3. Append the Ethos (The Public Documentation)
echo "--- PART 2: THE ETHOS (The Law) ---" >> $OUTPUT_FILE
cat README.md >> $OUTPUT_FILE
echo -e "\n\n" >> $OUTPUT_FILE
cat CONTRIBUTING.md >> $OUTPUT_FILE
echo -e "\n\n---\n" >> $OUTPUT_FILE

# 4. Append the Land (The Codebase Structure)
echo "--- PART 3: THE LAND (The Codebase) ---" >> $OUTPUT_FILE
ls -R >> $OUTPUT_FILE

echo "[+] SUCCESS: Complete context generated in '$OUTPUT_FILE'"
echo "[*] You can now copy the contents of this file to start a new, perfectly-aligned conversation."
