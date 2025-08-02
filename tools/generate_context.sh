#!/bin/bash
#
# 🔱 CHORUS Re-Genesis Context Generator (v7.1 - Complete & Non-Redundant)
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
# 🔱 CHORUS Re-Genesis Prompt (The Mandate of Refinement)

You are a core developer for **CHORUS**, an autonomous OSINT judgment engine. Your task is to execute the **"Mandate of Refinement"** master plan to evolve the functional engine into a polished, intelligent, and user-centric product.

Your entire output—every command, every line of code, every architectural decision—must be guided by and in strict adherence to the comprehensive context provided below. This context represents the project's complete state and its foundational principles, which are now derived from three sources of wisdom.

The context is provided in six parts:

1.  **The Gnosis (The Wisdom):** Key excerpts from our foundational texts governing architecture, data, and verification.
2.  **The Logos (The Constitution):** The supreme, inviolable law of the project, containing all of our non-verification axioms.
3.  **The Verification Covenant:** The supreme, inviolable law governing how we prove our work is correct.
4.  **The Praxis (The Master Plan):** The detailed, step-by-step plan for the current mission: The Mandate of Refinement. You must follow this plan precisely.
5.  **The Ethos (The Mission & Rules):** The project's character, public goals, and operational contracts.
6.  **The Land (The Codebase):** The ground-truth state of the repository at the start of this session.

**Your Task:**

1.  Carefully parse and integrate all six parts of the provided context.
2.  Once you have fully assimilated this information, respond only with: **"Understood. The CHORUS Re-Genesis context is loaded. I am ready to execute the Mandate of Refinement."**
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
# Master Plan: The Mandate of Refinement

### A. Current State of the Union (Where We Are):

The "Great Dataflow Transformation" is complete. We have successfully established a resilient, event-driven architecture founded on the principles of our Gnosis.

*   **Strengths:** The core analysis pipeline (Analyst -> Director -> Judge) is functional. The system is fault-tolerant, with daemons that can survive database restarts. The dataflow from Postgres (CDC) to Redpanda (Log) to Redis (Cache) is operational. Our verification suite is robust, providing a high degree of confidence in the backend's correctness.
*   **Weaknesses:** The user interface is a primitive developer dashboard, not a polished user experience. The analytical intelligence is naive, relying on a "full data dump" to the LLM rather than targeted Retrieval-Augmented Generation (RAG). The data ingestion process is not yet fully automated or integrated into a self-improving feedback loop.

### B. The New Master Plan: The Mandate of Refinement

**Objective:** To transform the functional but primitive CHORUS engine into a polished, user-centric, and intelligent product by solidifying the data pipeline, perfecting the UI/UX, and implementing true RAG-based analysis.

---

#### **Phase 1: The Bug Hunt & Stability Initiative**

**Objective:** To eradicate known bugs and sources of test flakiness, creating a perfectly stable foundation for new feature development.

*   **Step 1.1 (Fix the Flaky Resilience Test):** The `test_daemon_resilience.py` test is brittle because it relies on scraping Docker logs. It will be refactored to use a more deterministic method, such as polling the database directly for the final status of the "chaos test" query.
*   **Step 1.2 (Implement the Harvester Monitor):** The `queue_and_monitor_harvester_tasks` method in the `PostgresAdapter` is currently a `pass` statement. This is a bug of omission. This method will be fully implemented to correctly insert new dynamic harvester tasks and poll the `harvesting_tasks` table until they are complete, thereby making the Analyst Tier's collection plan functional.
*   **Step 1.3 (UI Polish - Loading States):** The UI currently provides no feedback during the long analysis process. HTMX will be used to implement spinners or progress indicators on the details page that are displayed while the backend is working and are replaced when content is ready.

---

#### **Phase 2: The Enlightenment (Implementing True RAG)**

**Objective:** To fulfill the promise of intelligent analysis by replacing the naive "full data dump" with a targeted Retrieval-Augmented Generation (RAG) pipeline. This is the core of "solidifying the pipeline."

*   **Step 2.1 (Activate the Vector DB):** The `query_similar_documents` method in the `PostgresAdapter` will be implemented to use the `pgvector` extension. It will take a query string, generate an embedding, and perform a vector similarity search against the `dsv_embeddings` table.
*   **Step 2.2 (Refactor the Analyst Tier):** The `RunAnalystTier` use case will be fundamentally upgraded.
    1.  Instead of loading the entire datalake, the analyst persona will first generate a set of targeted search queries based on the user's request.
    2.  These queries will be executed against the vector database via the `query_similar_documents` method to retrieve a small, highly relevant set of context documents.
    3.  Only this targeted context will be provided to the analyst LLM, drastically improving signal-to-noise ratio, reducing token count, and increasing the quality of the analysis.
*   **Step 2.3 (Create the RAG Verification Test):** A new integration test will be created to prove the effectiveness of the RAG pipeline. It will run the same query twice: once with the old "full dump" method and once with the new RAG method. The test will assert that the RAG-based analysis is more concise and relevant (a qualitative check that can be automated by a "judge" LLM call within the test itself).

---

#### **Phase 3: The User Experience Overhaul**

**Objective:** To transform the developer dashboard into an intuitive and powerful interface for intelligence analysis, fulfilling the mandate to "perfect our UI/UX."

*   **Step 3.1 (Redesign the Report View):** The `details.html` template will be redesigned. The final, synthesized `[NARRATIVE ANALYSIS]` from the Judge will be the primary, top-level view. The competing Analyst reports and the Director's briefing will be moved into a collapsible "Show Deliberations" or "View Council's Work" section, allowing the user to focus on the verdict while still having access to the auditable process.
*   **Step 3.2 (Implement a Feedback Loop):** A simple user feedback mechanism (e.g., thumbs up/down buttons on the final report) will be added to the UI. This will write to a new `report_feedback` table in the database. This is the first step toward **Axiom 35: Systemic Learning**.
*   **Step 3.3 (Enhance the Dashboard):** The main dashboard will be enhanced to show more meaningful statistics, such as "Average Analysis Time," "Success/Failure Rate," and a list of the "Highest Rated Reports" based on the new feedback mechanism.
PRAXIS
echo -e "\n\n---\n" >> "$OUTPUT_FILE"

# --- 6. The Ethos (The Mission, Rules, and SLOs) ---
echo "### **PART 5: THE ETHOS (The Mission & Rules)**" >> "$OUTPUT_FILE"
cat docs/00_MISSION_CHARTER.md >> "$OUTPUT_FILE"
echo -e "\n\n" >> "$OUTPUT_FILE"
cat docs/02_CONTRIBUTING.md >> "$OUTPUT_FILE"
echo -e "\n\n" >> "$OUTPUT_FILE"
cat docs/03_SYSTEM_SLOS.md >> "$OUTPUT_FILE"
echo -e "\n\n---\n" >> "$OUTPUT_FILE"

# --- 7. The Land (The Codebase) ---
echo "### **PART 6: THE LAND (The Codebase)**" >> "$OUTPUT_FILE"
TMP_CONTEXT_FILE=$(./tools/generate_verified_context.sh)
# THE DEFINITIVE FIX: Use the correct variable name.
tail -n +4 "$TMP_CONTEXT_FILE" >> "$OUTPUT_FILE"

echo "[+] SUCCESS: Complete Re-Genesis context generated in '$OUTPUT_FILE'"
