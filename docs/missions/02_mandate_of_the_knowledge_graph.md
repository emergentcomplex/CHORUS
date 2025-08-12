# Idea 02: Implement a Navigable, Auditable Database Schema

**1. Concept:**
Overhaul the core database schema to transform it from a simple data store into a relational, hierarchical model of our entire analytical process. The goal is to create a structure that allows a user (or a future AI auditor) to intuitively "zoom" from a high-level analysis session down to the atomic metadata of a single LLM call. This will be enhanced by leveraging MariaDB's native System-Versioning for our `personas` table to create a perfect, reversible audit trail of all cognitive changes.

**2. Problem Solved:**

- **Lack of Navigability:** The current schema is flat, making it impossible to trace the relationship between a Director's task and its subordinate Analyst tasks, or to link a specific LLM call to the persona and step that generated it.
- **Poor Auditability & Reproducibility:** Without a clear relational structure and a history of persona definitions, it is impossible to reconstruct the "Chain of Justification" for a report or to reproduce an old analysis with the exact cognitive model that was active at the time.
- **UI Limitations:** The flat schema prevents us from building a sophisticated UI that can visualize the entire, multi-layered analytical workflow.

**3. Proposed Solution:**
This will be implemented via a significant refactoring of the `schema.sql` file and a corresponding overhaul of all scripts that interact with the database.

- **A. The New Relational Schema:**

  - **`analysis_sessions`:** A new, top-level table for each user query.
  - **`tasks`:** A new, generic table to replace the `task_queue`, featuring a `parent_task_id` to create the Director -> Analyst tree structure.
  - **`llm_calls`:** A new table to replace `prompt_log`, with each record explicitly linked to the `task_id` that initiated it.
  - **`personas` (System-Versioned):** The `personas` table will be recreated `WITH SYSTEM VERSIONING`. This delegates the entire history tracking of persona changes to the database engine itself, making it robust and efficient. The complex, application-level `cognitive_ledger` table is no longer needed.

- **B. The "Zoomable" User Interface:**

  - The UI will be redesigned to follow this new relational model, allowing a user to navigate from a session, down to its constituent tasks, and further down to the individual LLM calls made by each task.

- **C. Temporally-Aware Persona Loading:**
  - The `persona_worker` and `director_worker` will be refactored. When a task begins, they will use the `created_at` timestamp of the parent `analysis_session` to fetch the correct historical version of their persona from the system-versioned `personas` table.
  - This is achieved with a temporal query: `SELECT ... FROM personas FOR SYSTEM_TIME AS OF 'session_creation_timestamp' WHERE ...`.
  - This implements the **Axiom of Temporal Self-Awareness**, guaranteeing perfect reproducibility of any past analysis.

**4. Next Steps:**

- This is a **foundational prerequisite for Phase 2**. The hierarchical task structure is essential for the Director/Analyst workflow.
- It requires a formal Amendment Proposal to the Constitution to:
  - Completely overhaul the database schema described in the "Codebase Architecture" section.
  - Add the "Axiom of Auditable AI" and the "Axiom of Reversible Cognition."
- The implementation will be a major refactoring effort, touching the schema, all worker scripts, and the entire web UI.
