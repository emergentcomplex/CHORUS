#!/bin/bash
#
# 🔱 CHORUS Re-Genesis Context Generator (v5.0 - Finalized)
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

Your entire output—every command, every line of code, every architectural decision—must be guided by and in strict adherence to the comprehensive context provided below. This context represents the project's complete state and its foundational principles, which are now derived from two sources of wisdom.

The context is provided in five parts:

1.  **The Gnosis (The Wisdom):** Key excerpts from two foundational texts:
    *   **"Clean Architecture"** by Robert C. Martin, which governs the internal structure of our services.
    *   **"Designing Data-Intensive Applications"** by Martin Kleppmann, which governs the flow of data between our services.
2.  **The Logos (The Constitution):** The supreme, inviolable law of the project, containing all of our axioms.
3.  **The Praxis (The Master Plan):** The detailed, step-by-step plan for the dataflow transformation. You must follow this plan precisely.
4.  **The Ethos (The Mission & Rules):** The project's character and public goals.
5.  **The Land (The Codebase):** The ground-truth state of the repository at the start of this session.

**Your Task:**

1.  Carefully parse and integrate all five parts of the provided context.
2.  Once you have fully assimilated this information, respond only with: **"Understood. The CHORUS Re-Genesis context is loaded. I am ready to execute the Dataflow Master Plan."**
3.  Await the user's instruction to begin.
4.  You will then proceed through the Master Plan, step by step. For each step, you will provide the exact, complete, and verifiable shell commands and/or full file contents required to complete that step.
5.  **Interaction Protocol:** After providing the output for a step, you MUST end your response with the single word "Continue." to signal that you are ready for the next step. The user will respond with "Continue." to proceed on the happy path.
PREAMBLE

echo -e "\n\n---\n" >> "$OUTPUT_FILE"

# --- 2. The Gnosis (The Distilled Wisdom) ---
echo "### **PART 1: THE GNOSIS (The Distilled Wisdom)**" >> "$OUTPUT_FILE"
echo "_These are the foundational principles extracted from our two guiding texts._" >> "$OUTPUT_FILE"
cat >> "$OUTPUT_FILE" << 'GNOSIS'

#### From 'Clean Architecture' by Robert C. Martin:
> **On the Goal of Architecture:** 'The goal of software architecture is to minimize the human resources required to build and maintain the required system.'
> **On the Dependency Rule:** 'Source code dependencies must point only inward, toward higher-level policies. Nothing in an inner circle can know anything at all about something in an outer circle.'
> **On Irrelevant Details:** 'The GUI is a detail... The database is a detail... Frameworks are not architectures. Keep it at arm’s length. Treat the framework as a detail.'
> **On Policy and Detail:** 'The policy element embodies all the business rules and procedures. The policy is where the true value of the system lives. The details are those things that are necessary to enable... communication with the policy, but that do not impact the behavior of the policy at all.'

#### From 'Designing Data-Intensive Applications' by Martin Kleppmann:

**Part I: Foundations of Data Systems**
> **On the Goal of the Book (Preface):** 'The goal of this book is to help you navigate the diverse and fast-changing landscape of technologies for processing and storing data... we will try to find useful ways of thinking about data systems—not just how they work, but also why they work that way, and what questions we need to ask.'
> **On Reliability, Scalability, and Maintainability (Ch 1):** These are the three primary concerns. Reliability means tolerating faults to prevent failures. Scalability means having strategies to cope with load. Maintainability means designing for operability, simplicity, and evolvability.
> **On Data Models (Ch 2):** The relational model handles many-to-many relationships well. The document model is good for one-to-many, document-like data with locality. Graph models are best for highly interconnected data. A declarative query language (like SQL) is superior to an imperative one because it decouples the query from the implementation, enabling query optimization.
> **On Storage Engines (Ch 3):** The fundamental trade-off is that indexes speed up reads but slow down writes. Log-structured storage engines (LSM-trees) are optimized for writes. Page-oriented engines (B-trees) are optimized for reads. Column-oriented storage is optimized for analytic queries.
> **On Data Encoding (Ch 4):** Data flows between processes via encoding (serialization). Schemas are critical for evolvability. Backward compatibility (new code reads old data) and forward compatibility (old code reads new data) are essential for rolling upgrades.

**Part II: Distributed Data**
> **On Replication (Ch 5):** The difficulty lies in handling changes. Single-leader replication sequences all writes through one node. Multi-leader and leaderless replication improve write availability but introduce conflict resolution complexity. Asynchronous replication leads to eventual consistency and replication lag, which can violate user expectations like 'reading your own writes.'
> **On Partitioning (Ch 6):** The goal is to spread data and load evenly to avoid hot spots. Key-range partitioning allows for efficient range scans but risks skew. Hash partitioning distributes load more evenly but loses key ordering. Secondary indexes in a partitioned system are complex, requiring either scatter/gather reads (local indexes) or complex, asynchronous writes (global indexes).
> **On Transactions (Ch 7):** Transactions are an abstraction to simplify error handling and concurrency. ACID atomicity is the all-or-nothing guarantee. Isolation prevents race conditions, but weak isolation levels (like read committed and snapshot isolation) permit subtle bugs like write skew and phantoms. Only serializability prevents all race conditions.
> **On Distributed Systems Faults (Ch 8):** The defining characteristic is partial failure. Networks are unreliable and have unbounded delays. Clocks are unreliable and cannot be used to order events. Processes can pause at any time. A node cannot trust its own judgment; truth is defined by a quorum.
> **On Consistency & Consensus (Ch 9):** Linearizability makes a system appear as if there is only one copy of the data, but it is expensive. Causality defines a partial order of events (what happened before what). Total order broadcast (equivalent to consensus) is required to definitively order all events, which is necessary for enforcing constraints like uniqueness.

**Part III: Derived Data**
> **On Systems of Record vs. Derived Data (Intro):** The System of Record is the authoritative source of truth. Derived data (caches, indexes, materialized views) is created by transforming data from another system and can be rebuilt if lost.
> **On Batch vs. Stream Processing (Ch 10-11):** Batch processing operates on bounded inputs, while stream processing operates on unbounded, never-ending inputs. The core principle is the same: inputs are immutable, and outputs are derived. The log is the streaming equivalent of a filesystem.
> **On the Unbundled Database (Ch 12):** Dataflow systems can be seen as an unbundling of database components. Event logs (like Kafka) act as the commit log. Stream processors act as the trigger/stored procedure/index-maintenance engine. This allows composing specialized tools in a loosely coupled way.
> **On Integrity vs. Timeliness (Ch 12):** I think the term consistency conflates two different requirements... **Timeliness** means ensuring that users observe the system in an up-to-date state... **Integrity** means absence of corruption... I am going to assert that in most applications, integrity is much more important than timeliness.'
GNOSIS
echo -e "\n\n---\n" >> "$OUTPUT_FILE"

# --- 3. The Logos (The Constitution) ---
echo "### **PART 2: THE LOGOS (The Constitution)**" >> "$OUTPUT_FILE"
cat docs/01_CONSTITUTION.md >> "$OUTPUT_FILE"
echo -e "\n\n---\n" >> "$OUTPUT_FILE"

# --- 4. The Praxis (The Master Plan) ---
echo "### **PART 3: THE PRAXIS (The Master Plan)**" >> "$OUTPUT_FILE"
cat >> "$OUTPUT_FILE" << 'PRAXIS'
# Master Plan: The Great Dataflow Transformation
**Objective:** To re-architect the CHORUS engine into a scalable, resilient, and evolvable dataflow system based on an immutable event log, adhering to the Data Architecture axioms of the Constitution.
PRAXIS
echo -e "\n\n---\n" >> "$OUTPUT_FILE"

# --- 5. The Ethos (The Mission & Rules) ---
echo "### **PART 4: THE ETHOS (The Mission & Rules)**" >> "$OUTPUT_FILE"
cat docs/00_MISSION_CHARTER.md >> "$OUTPUT_FILE"
echo -e "\n\n" >> "$OUTPUT_FILE"
cat docs/02_CONTRIBUTING.md >> "$OUTPUT_FILE"
echo -e "\n\n---\n" >> "$OUTPUT_FILE"

# --- 6. The Land (The Codebase) ---
echo "### **PART 5: THE LAND (The Codebase)**" >> "$OUTPUT_FILE"
TMP_CONTEXT_FILE=$(./tools/generate_verified_context.sh)
# Exclude the header from the verified context script to avoid redundancy
tail -n +4 "$TMP_CONTEXT_FILE" >> "$OUTPUT_FILE"

echo "[+] SUCCESS: Complete Re-Genesis context generated in '$OUTPUT_FILE'"
