#!/bin/bash
#
# 🔱 CHORUS Re-Genesis Context Generator (v13 - Explicit & Final)
#
# Gathers all necessary context, including our codified failures, to ensure
# the next development session starts from a state of maximum knowledge.

set -e

# Navigate to the project root directory
cd "$(dirname "$0")/.."

# --- Praxis File Argument ---
PRAXIS_FILE=$1
if [ -z "$PRAXIS_FILE" ] || [ ! -f "$PRAXIS_FILE" ]; then
    echo "[!] ERROR: You must provide a valid path to a mission brief."
    echo "    Usage: $0 docs/ideas/00_mandate_of_final_separation.md"
    exit 1
fi

OUTPUT_FILE="CONTEXT_FOR_AI.txt"
echo "[*] Generating Re-Genesis context for CHORUS..."
echo "[*] Using mission brief: $PRAXIS_FILE"

# --- 1. The Genesis Prompt (The Preamble) ---
cat > "$OUTPUT_FILE" << 'PREAMBLE'
# 🔱 CHORUS Re-Genesis Prompt (The Mandate of Refinement)

You are a core developer for **CHORUS**, an autonomous OSINT judgment engine. Your task is to execute the Master Plan provided in the Praxis section below.

Your entire output—every command, every line of code, every architectural decision—must be guided by and in strict adherence to the comprehensive context provided below. This context represents the project's complete state, its foundational principles, and the codified lessons from its past failures.

The context is provided in seven parts:

1.  **The Gnosis (The Wisdom):** Key excerpts from our foundational texts.
2.  **The Logos (The Constitution):** The supreme, inviolable law of the project.
3.  **The Verification Covenant:** The supreme, inviolable law governing how we prove our work.
4.  **The Graveyard (The Lessons):** A list of failed hypotheses and anti-patterns that MUST be avoided.
5.  **The Praxis (The Master Plan):** The detailed, step-by-step plan for the current mission.
6.  **The Ethos (The Mission & Rules):** The project's character, public goals, and operational contracts.
7.  **The Land (The Codebase):** The ground-truth state of the repository.

**Your Task:**

1.  Carefully parse and integrate all seven parts of the provided context. Pay special attention to The Graveyard to avoid repeating past failures.
2.  Once you have fully assimilated this information, respond only with: **"Understood. The CHORUS Re-Genesis context is loaded. I am ready to execute the Master Plan."**
3.  Await the user's instruction to begin.
4.  You will then proceed through the Master Plan, step by step. For each step, you will provide the exact, complete, and verifiable shell commands and/or full file contents required to complete that step.
5.  **Interaction Protocol:** After providing the output for a step, you MUST end your response with the single word "Continue." to signal that you are ready for the next step. The user will respond with "Continue." to proceed on the happy path.
PREAMBLE

echo -e "\n\n---\n" >> "$OUTPUT_FILE"

# --- 2. The Gnosis, Logos, Covenant, Graveyard, Praxis, Ethos ---
echo "### **PART 1: THE GNOSIS (The Distilled Wisdom)**" >> "$OUTPUT_FILE"
cat docs/00_GNOSIS.md >> "$OUTPUT_FILE"
echo -e "\n\n---\n" >> "$OUTPUT_FILE"

echo "### **PART 2: THE LOGOS (The Constitution)**" >> "$OUTPUT_FILE"
cat docs/01_CONSTITUTION.md >> "$OUTPUT_FILE"
echo -e "\n\n---\n" >> "$OUTPUT_FILE"

echo "### **PART 3: THE VERIFICATION COVENANT**" >> "$OUTPUT_FILE"
cat docs/04_VERIFICATION_COVENANT.md >> "$OUTPUT_FILE"
echo -e "\n\n---\n" >> "$OUTPUT_FILE"

echo "### **PART 4: THE GRAVEYARD (The Lessons)**" >> "$OUTPUT_FILE"
cat docs/05_FAILED_HYPOTHESES.md >> "$OUTPUT_FILE"
echo -e "\n\n---\n" >> "$OUTPUT_FILE"

echo "### **PART 5: THE PRAXIS (The Master Plan)**" >> "$OUTPUT_FILE"
cat "$PRAXIS_FILE" >> "$OUTPUT_FILE"
echo -e "\n\n---\n" >> "$OUTPUT_FILE"

echo "### **PART 6: THE ETHOS (The Mission & Rules)**" >> "$OUTPUT_FILE"
cat docs/00_MISSION_CHARTER.md >> "$OUTPUT_FILE"
echo -e "\n\n" >> "$OUTPUT_FILE"
cat docs/02_CONTRIBUTING.md >> "$OUTPUT_FILE"
echo -e "\n\n" >> "$OUTPUT_FILE"
cat docs/03_SYSTEM_SLOS.md >> "$OUTPUT_FILE"
echo -e "\n\n---\n" >> "$OUTPUT_FILE"

# --- 7. The Land (The Codebase) ---
echo "### **PART 7: THE LAND (The Codebase)**" >> "$OUTPUT_FILE"

TMP_CONTEXT_FILE=$(./tools/generate_verified_context.sh)
trap 'rm -f "$TMP_CONTEXT_FILE"' EXIT
cat "$TMP_CONTEXT_FILE" >> "$OUTPUT_FILE"

echo "[+] SUCCESS: Complete, lesson-infused Re-Genesis context generated in '$OUTPUT_FILE'"
echo "    Mission: $(head -n 2 $PRAXIS_FILE)"