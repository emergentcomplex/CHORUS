# Idea 02: Implement a Navigable, Auditable Database Schema

**1. Concept:**
Overhaul the core database schema to transform it from a simple data store into a relational, hierarchical model of our entire analytical process. The goal is to create a structure that allows a user (or a future AI auditor) to intuitively "zoom" from a high-level analysis session down to the atomic metadata of a single LLM call.

**2. Problem Solved:**
- **Lack of Navigability:** The current schema is flat. A `task_queue` table holds all tasks, and a `prompt_log` table holds all LLM calls. It is impossible to determine which Analyst task belongs to which Director, or which LLM call was made by which specific persona in which specific step of their process.
- **Poor Auditability:** Without a clear relational structure, it is extremely difficult to reconstruct the "Chain of Justification" for a final report. We cannot easily see the full context—the prompts, the harvester results, the persona used—that led to a specific conclusion.
- **UI Limitations:** The flat schema prevents us from building a sophisticated user interface. We can only show a simple list of tasks, not a rich, interactive view of the entire analytical workflow.

**3. Proposed Solution:**
This will be implemented via a significant refactoring of the `schema.sql` file and a corresponding overhaul of all scripts that interact with the database, most notably the `web_ui.py` and all worker scripts.

- **A. The New Relational Schema:**
  - **`analysis_sessions`:** A new, top-level table. Each user query will create a single session, identified by a unique `session_id`. This is the root of the hierarchy.
  - **`tasks`:** A new, generic table to replace the `task_queue`. It will hold both Director and Analyst tasks. Each task will be linked to a `session_id` and will have a `parent_task_id`, allowing us to create the Director -> Analyst tree structure.
  - **`llm_calls`:** A new table to replace `prompt_log`. Each record will be explicitly linked to the `task_id` that initiated it. It will be upgraded to store the precise `input_tokens` and `output_tokens` for the call.
  - **`task_progress`:** This table will be updated to link its log messages to a specific `task_id` instead of a generic hash.

- **B. The "Zoomable" User Interface:**
  - The UI will be redesigned to follow this new relational model:
    - **Dashboard (Level 0):** Shows a list of all `analysis_sessions`.
    - **Session View (Level 1):** Clicking a session shows the Director task and its four subordinate Analyst tasks.
    - **Task View (Level 2):** Clicking a task shows its final report/brief, its progress log, and a summary of the LLM calls it made.
    - **LLM Call View (Level 3):** Clicking an LLM call opens a modal showing the full prompt, the full response, and all associated metadata (tokens, duration, etc.).

- **C. Worker Refactoring:**
  - All worker scripts (`director_worker`, `persona_worker`) will be updated to use the new schema. They will fetch tasks from the `tasks` table and log their progress and LLM calls with the correct `task_id`.
  - The `web_ui.py`'s `queue_new_query` function will be renamed `queue_new_session` and will create the initial entry in the `analysis_sessions` table.

**4. Next Steps:**
- This is a **foundational prerequisite for Phase 2**. The hierarchical task structure is essential for the Director/Analyst workflow.
- It requires a formal Amendment Proposal to the Constitution to:
  - Completely overhaul the database schema described in the "Codebase Architecture" section.
  - Add the "Axiom of Auditable AI" to codify the importance of this feature.
- The implementation will be a major refactoring effort, touching the schema, all worker scripts, and the entire web UI.
