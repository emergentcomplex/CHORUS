#!/bin/bash
#
# 🔱 CHORUS Re-Genesis Context Generator (v6.0 - Verification Covenant)
#
# Gathers all necessary context from the definitive /docs directory and
# the codebase to bootstrap an AI development session. This script is the
# canonical tool for starting a new development session.

set -e

# Navigate to the project root directory
cd "$(dirname "$0")/.."

OUTPUT_FILE="CONTEXT_FOR_AI.txt"
echo "[*] Generating Re-Genesis context for CHORUS from canonical docs..."

# --- Temporary file for the codebase snapshot ---
TMP_CONTEXT_FILE=""
trap 'rm -f "$TMP_CONTEXT_FILE"' EXIT

# --- 1. The Genesis Prompt (The Preamble) ---
cat > "$OUTPUT_FILE" << 'PREAMBLE'
# 🔱 CHORUS Re-Genesis Prompt (Data-Intensive)

You are a core developer for **CHORUS**, an autonomous OSINT judgment engine. Your task is to execute the "Great Dataflow Transformation" master plan to evolve the existing application into a scalable, resilient, and data-intensive architecture.

Your entire output—every command, every line of code, every architectural decision—must be guided by and in strict adherence to the comprehensive context provided below. This context represents the project's complete state and its foundational principles, which are now derived from three sources of wisdom.

The context is provided in six parts:

1.  **The Gnosis (The Wisdom):** Key excerpts from our foundational texts governing architecture, data, and verification.
2.  **The Logos (The Constitution):** The supreme, inviolable law of the project, containing all of our non-verification axioms.
3.  **The Verification Covenant:** The supreme, inviolable law governing how we prove our work is correct.
4.  **The Praxis (The Master Plan):** The detailed, step-by-step plan for the dataflow transformation. You must follow this plan precisely.
5.  **The Ethos (The Mission & Rules):** The project's character and public goals.
6.  **The Land (The Codebase):** The ground-truth state of the repository at the start of this session.

**Your Task:**

1.  Carefully parse and integrate all six parts of the provided context.
2.  Once you have fully assimilated this information, respond only with: **"Understood. The CHORUS Re-Genesis context is loaded. I am ready to execute the Dataflow Master Plan."**
3.  Await the user's instruction to begin.
4.  You will then proceed through the Master Plan, step by step. For each step, you will provide the exact, complete, and verifiable shell commands and/or full file contents required to complete that step.
5.  **Interaction Protocol:** After providing the output for a step, you MUST end your response with the single word "Continue." to signal that you are ready for the next step. The user will respond with "Continue." to proceed on the happy path.
PREAMBLE

echo -e "\n\n---\n" >> "$OUTPUT_FILE"

# --- 2. The Gnosis (The Distilled Wisdom) ---
echo "### **PART 1: THE GNOSIS (The Distilled Wisdom)**" >> "$OUTPUT_FILE"
echo "_These are the foundational principles extracted from our three guiding texts._" >> "$OUTPUT_FILE"
cat >> "$OUTPUT_FILE" << 'GNOSIS'

#### From 'Clean Architecture' by Robert C. Martin:
> **On the Goal of Architecture:** 'The goal of software architecture is to minimize the human resources required to build and maintain the required system.'
> **On the Dependency Rule:** 'Source code dependencies must point only inward, toward higher-level policies. Nothing in an inner circle can know anything at all about something in an outer circle.'
> **On Irrelevant Details:** 'The GUI is a detail... The database is a detail... Frameworks are not architectures. Keep it at arm’s length. Treat the framework as a detail.'

#### From 'Designing Data-Intensive Applications' by Martin Kleppmann:
> **On Reliability, Scalability, and Maintainability (Ch 1):** These are the three primary concerns. Reliability means tolerating faults to prevent failures. Scalability means having strategies to cope with load. Maintainability means designing for operability, simplicity, and evolvability.
> **On the Unbundled Database (Ch 12):** Dataflow systems can be seen as an unbundling of database components. Event logs (like Kafka) act as the commit log. Stream processors act as the trigger/stored procedure/index-maintenance engine. This allows composing specialized tools in a loosely coupled way.
> **On Integrity vs. Timeliness (Ch 12):** 'I am going to assert that in most applications, integrity is much more important than timeliness.'

#### From 'Unit Testing: Principles, Patterns, and Practices' by Vladimir Khorikov:
> **On the Goal of Unit Testing:** 'The goal of unit testing is to enable sustainable growth of a software project.'
> **On What to Test (Observable Behavior):** 'You should test only the observable behavior of the SUT (System Under Test)... An observable behavior is a behavior that can be perceived by the SUT’s clients.'
> **On Mocks vs. Stubs:** 'Remember this simple rule: stubs can’t fail tests; mocks can... Use mocks to verify interactions between the SUT and its collaborators. Use stubs to feed the SUT with data.'
> **On the Four Pillars of a Good Unit Test:** 'A good unit test has four attributes: 1. It provides protection against regressions. 2. It is resistant to refactoring. 3. It provides fast feedback. 4. It is maintainable.'
GNOSIS
echo -e "\n\n---\n" >> "$OUTPUT_FILE"

# --- 3. The Logos (The Constitution) ---
echo "### **PART 2: THE LOGOS (The Constitution)**" >> "$OUTPUT_FILE"
cat docs/01_CONSTITUTION.md >> "$OUTPUT_FILE"
echo -e "\n\n---\n" >> "$OUTPUT_FILE"

# --- 4. The Verification Covenant ---
echo "### **PART 3: THE VERIFICATION COVENANT**" >> "$OUTPUT_FILE"
cat docs/04_VERIFICATION_COVENANT.md >> "$OUTPUT_FILE"
echo -e "\n\n---\n" >> "$OUTPUT_FILE"

# --- 5. The Praxis (The Master Plan) ---
echo "### **PART 4: THE PRAXIS (The Master Plan)**" >> "$OUTPUT_FILE"
cat >> "$OUTPUT_FILE" << 'PRAXIS'
# Master Plan: The Great Dataflow Transformation
**Objective:** To re-architect the CHORUS engine into a scalable, resilient, and evolvable dataflow system based on an immutable event log, adhering to the Data Architecture axioms of the Constitution.
PRAXIS
echo -e "\n\n---\n" >> "$OUTPUT_FILE"

# --- 6. The Ethos (The Mission & Rules) ---
echo "### **PART 5: THE ETHOS (The Mission & Rules)**" >> "$OUTPUT_FILE"
cat docs/00_MISSION_CHARTER.md >> "$OUTPUT_FILE"
echo -e "\n\n" >> "$OUTPUT_FILE"
cat docs/02_CONTRIBUTING.md >> "$OUTPUT_FILE"
echo -e "\n\n---\n" >> "$OUTPUT_FILE"

# --- 7. The Land (The Codebase) ---
echo "### **PART 6: THE LAND (The Codebase)**" >> "$OUTPUT_FILE"
TMP_CONTEXT_FILE=$(./tools/generate_verified_context.sh)
# Exclude the header from the verified context script to avoid redundancy
tail -n +4 "$TMP_CONTEXT_FILE" >> "$OUTPUT_FILE"

echo "[+] SUCCESS: Complete Re-Genesis context generated in '$OUTPUT_FILE'"
