# 🔱 Praxis: The Mandate of the Forge

## I. Objective

To execute the blueprint created by the "Mandate of Gnosis." This mission is a pure implementation task to build the full suite of tools and database schemas required to make the new, formalized System Lifecycle Protocol operational. This will transform our development process from an informal practice into a measurable, high-velocity engineering discipline.

## II. Justification

With the design and philosophy now codified in our governing documents (`00_THE_CONSTITUTION.md` and `07_THE_DEVELOPMENT_PROTOCOL.md`), this mission translates that vision into verifiable, working code. It builds the factory according to the approved blueprints, enabling us to manage our work in small batches, make our process visible, and track our performance against the Four Key Metrics.

## III. The Plan

This mission will be executed in three distinct, verifiable sub-phases.

- **Sub-Phase 1: Implement the Data Layer for Process Management**

  - **Task:** Modify the database schema to support the new lifecycle protocol.
  - **Action:** Edit `infrastructure/postgres/init.sql` to add two new tables:
    - `mission_ledger`: A table to track the state of all development missions (e.g., `mission_name`, `status`, `start_time`, `end_time`, `pr_url`).
    - `datalake_processed_files`: A stateful table for the `vectorizer` daemon to track which files from the datalake have already been processed, preventing redundant work.

- **Sub-Phase 2: Implement the Forge Toolkit**

  - **Task:** Create the command-line tools for managing the mission lifecycle.
  - **Action:** Create a new directory: `tools/forge/`.
  - **Action:** Inside `tools/forge/`, create the following scripts:
    - `begin_mission.sh`: Takes a mission name, creates a new topic branch, and adds a "PENDING" entry to the `mission_ledger`.
    - `generate_commit_message.py`: A helper script that takes a mission name and generates a structured, conventional commit message.
    - `succeed_mission.sh`: Merges the current branch to main, pushes, and updates the mission's status to "SUCCEEDED" in the `mission_ledger`.
    - `fail_mission.sh`: Abandons the current mission, cleans up the branch, and updates the status to "FAILED".
  - **Action:** Update the `Makefile` to add new, user-friendly targets that call these scripts (e.g., `make mission-begin`, `make mission-succeed`).

- **Sub-Phase 3: Implement Data Lifecycle Policies**
  - **Task:** Implement the policies required by our Data Stratification axioms.
  - **Action:** Refactor the `vectorizer.py` daemon to use the new `datalake_processed_files` table to ensure it only processes each file once.
  - **Action:** Implement a log rotation policy for all containerized services to fulfill the pruning requirement for File State.

## IV. Acceptance Criteria

- **AC-1 (Schema):** The `mission_ledger` and `datalake_processed_files` tables are successfully created when the database is initialized.
- **AC-2 (Toolkit):** The `make mission-begin` and `make mission-succeed` targets are functional and correctly interact with both Git and the `mission_ledger` table.
- **AC-3 (Stateful Vectorizer):** A new integration test proves that the `vectorizer` daemon does not re-process a file that is already listed in the `datalake_processed_files` table.
- **AC-4 (Protocol Simulation):** A full, end-to-end simulation of the new protocol passes:
  1.  `make mission-begin` is run.
  2.  A small, verifiable code change is made.
  3.  The change is committed.
  4.  `make test` passes.
  5.  `make mission-succeed` is run, and the change is successfully merged to `main`.
- **AC-5 (Final Verification):** The final `make test` command completes with 100% success after all changes are implemented.
