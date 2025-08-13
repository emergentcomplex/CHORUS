# 🔱 Praxis: The Mandate of the Forge (v5, System Lifecycle Protocol)

## I. Objective

To design and implement a complete, formalized, and automated **System Lifecycle Protocol** for the CHORUS project. This mission will create a canonical, database-driven **Mission Ledger** to manage our strategic roadmap, build a suite of Git-native tools to govern the mission workflow, and implement a formal **Data Lifecycle and Provenance Protocol** to manage all expanding data stores within the system.

## II. Justification

Our previous missions have proven that an ad-hoc development process is a critical point of failure. This mission will build the "factory"—a robust, automated, and evidence-based system for creating and managing our work. The centerpiece of this factory will be a database-driven Mission Ledger and a suite of data management tools, which transform our roadmap and data stores from fragile, unmanaged artifacts into a queryable, stateful, and robust ecosystem. This is the definitive implementation of **Axiom 49 (Deliberate Velocity)**.

## III. Guiding Precepts & Inviolable Constraints

This mission will be guided by the synthesized wisdom of our canonical texts.

**A. The "Accelerate" Precept (The Logos):** Our protocol will be engineered to optimize the Four Key Metrics, favoring small, atomic batches (one mission per feature branch) and a fast, automated verification pipeline.

**B. The "Phoenix Project" Precept (The Pathos):** Our protocol will be designed to make work visible (via the Mission Ledger), identify and eliminate bottlenecks, and manage work-in-progress to ensure a fast, smooth flow.

**C. The "Pro Git" Precept (The Praxis):** Our protocol will be Git-native. The `make` targets we create will be elegant, idiomatic expressions of Git's core mechanics.

**D. The "Team Topologies" Precept (The Ethos):** Our protocol will serve as the formal, well-defined "API" between the **Human Operator (Enabling Team)** and the **AI Developer (Stream-Aligned Team)**.

**E. The "Data Stratification" Precept (The Foundation):** Our tooling **MUST** recognize and correctly manage the different strata of data as defined by **Axiom 25**. The protocol we build will be the first and most critical implementation of this new constitutional principle.

## IV. The Ground Truth (The Current State)

1.  **Stable `main` Branch:** The `main` branch is in a clean, reorganized, and fully verifiable state.
2.  **Ad-Hoc Workflow:** All Git operations and mission planning are currently manual.
3.  **Unmanaged Data Lifecycles:** There are no automated policies for managing the indefinite expansion of the Datalake, application logs, or other stateful files.

## V. The Plan

### **Phase 1: Assimilation and Protocol Design**

1.  **Sub-Phase 1.1: The Assimilation:**

    - **Action:** The operator will provide the core insights from the four guiding texts: "Accelerate," "The Phoenix Project," "Pro Git," and "Team Topologies."

2.  **Sub-Phase 1.2: The Blueprint**
    - **Action:** Synthesize the assimilated knowledge into a new, canonical document: `docs/07_THE_DEVELOPMENT_PROTOCOL.md`.
    - **Content:** This document will define the Mission Ledger, the full state transition diagram of the lifecycle, the formal Data Lifecycle Policies (pruning, rotation), and the function of each new tool.

### **Phase 2: The Forge Toolkit (Implementation)**

All new scripts will reside in a new `tools/forge/` directory.

1.  **Sub-Phase 2.1: The Mission Ledger (Database Edition)**

    - **Action:** Add a `CREATE TABLE mission_ledger` statement to `infrastructure/postgres/init.sql`.
    - **Schema:** `id (INT)`, `title (TEXT)`, `status (VARCHAR)`, `praxis_file (VARCHAR)`.
    - **Action:** Create `tools/forge/plan_missions.py`. This will be a database client for managing the ledger with subcommands like `--list`, `--archive`, and `--renumber`.

2.  **Sub-Phase 2.2: The Data Lifecycle Toolkit**

    - **Action:** Implement a **Log Rotation Policy**. Modify the Gunicorn startup commands and Python logging configurations to use a `RotatingFileHandler`, ensuring logs are automatically managed by size and count.
    - **Action:** Create `tools/forge/prune_datalake.sh`. This script will implement our 30-day retention policy for raw datalake files.
    - **Action:** Implement the **Vectorizer State in DB**. Add a `datalake_processed_files` table to `init.sql` and modify the `vectorizer.py` daemon to use this table instead of the `.vectorizer_log` file.

3.  **Sub-Phase 2.3: The Genesis & Adjournment Commands**
    - **Action:** Create the full suite of adjournment and GitFlow scripts (`begin_mission.sh`, `succeed_mission.sh`, `generate_commit_message.py`, `archive_impasse.sh`, `abort_mission.sh`, `request_review.sh`, `merge_mission.sh`).
    - **Integration:** These scripts will be built to interact with the new database-driven `mission_ledger` to read mission context and update status on completion.

### **Phase 3: The Master Orchestrator (The Makefile)**

1.  **Action:** Add the new `mission-*` targets to the `Makefile`.
2.  **Action:** Add a new `prune-datalake` target that calls the pruning script.

### **Phase 4: Documentary Re-Genesis**

1.  **Sub-Phase 4.1: Constitutional Amendment**

    - **Action:** Add the new **Axiom 25 (Data Stratification)** to `docs/00_THE_CONSTITUTION.md` and re-number all subsequent axioms.
    - **Action:** Add the new section, "IX. Principles of Mission Lifecycle Governance," and Axioms 85 through 88.

2.  **Sub-Phase 4.2: Regenerate Core Documents**
    - **Action:** After all tooling is complete, I will perform a full re-generation of `README.md`, `docs/01_THE_MISSION.md`, and `docs/05_THE_CONTRIBUTING_GUIDE.md` to reflect the new, formalized protocol and data policies.

## VI. Acceptance Criteria

- **AC-1:** The new canonical document, `docs/07_THE_DEVELOPMENT_PROTOCOL.md`, exists and fully describes the new lifecycle and data policies.
- **AC-2:** The `mission_ledger` and `datalake_processed_files` tables are added to the database schema.
- **AC-3:** All `tools/forge/` scripts are created and functional, correctly interacting with the database where required.
- **AC-4:** The `Makefile` is updated with all new `mission-*` and `prune-datalake` targets.
- **AC-5:** The `00_THE_CONSTITUTION.md` is successfully amended with the new Axiom of Data Stratification and the Mission Lifecycle Governance axioms.
- **AC-6:** All core documents (`README.md`, etc.) are successfully regenerated to reflect the new, formalized protocol.
- **AC-7 (The Final Verification):** A full, end-to-end simulation of the protocol is successfully executed, proving the entire system is functional and documented.
