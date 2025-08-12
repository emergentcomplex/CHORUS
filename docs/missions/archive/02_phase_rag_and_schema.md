# Praxis: The Enlightenment (Phase 2)

### Objective
To implement the definitive, three-tiered LLM architecture and overhaul the database schema, creating a navigable, auditable model of our analytical process. This will serve as the foundation for a true Retrieval-Augmented Generation (RAG) pipeline.

### Justification
This phase combines the original "Enlightenment" plan with the foundational prerequisites from our prior ideas (`Idea 01` & `Idea 02`). A true RAG pipeline is impossible without a sophisticated, multi-tiered LLM strategy and a database schema that can model the hierarchical nature of the analysis. This phase builds that foundation.

### The Plan

*   **Subphase 2.1 (The Three-Tiered LLM Architecture):**
    *   **Task:** Implement "The Directorate Standard" (`Idea 01`).
    *   **Implementation:** Refactor the `LLMClient` to manage a pool of clients for Utility, Synthesis, and Apex model tiers, configured via the `.env` file. All worker scripts will be updated to call the appropriate model tier for their specific task.
    *   **File(s) to Modify:** `LLMClient`, all worker scripts, `.env.example`.

*   **Subphase 2.2 (The Navigable, Auditable Database Schema):**
    *   **Task:** Overhaul the core database schema to be relational and hierarchical (`Idea 02`).
    *   **Implementation:** Refactor `schema.sql` to introduce `analysis_sessions`, a hierarchical `tasks` table with `parent_task_id`, and a dedicated `llm_calls` table. The `personas` table will be recreated `WITH SYSTEM VERSIONING` to enable perfect, reversible audit trails of cognitive changes.
    *   **File(s) to Modify:** `infrastructure/postgres/init.sql`, all database adapter methods, all worker scripts.

*   **Subphase 2.3 (The Vector Core Awakens):**
    *   **Task:** Activate the `query_similar_documents` method in the `PostgresAdapter`.
    *   **Implementation:** Implement the method to use `pgvector` to perform cosine similarity searches against the `dsv_embeddings` table.
    *   **File(s) to Modify:** `chorus_engine/adapters/persistence/postgres_adapter.py`.

*   **Subphase 2.4 (The Analyst's New Mind):**
    *   **Task:** Re-architect the `RunAnalystTier` to use the new RAG capability.
    *   **Implementation:** The use case will be changed to a three-step process: 1. **Query Formulation** (Utility Model), 2. **Context Retrieval** (Vector Core), and 3. **Insight Synthesis** (Synthesis Model).
    *   **File(s) to Modify:** `chorus_engine/app/use_cases/run_analyst_tier.py`.

### Definition of Done
1.  The `LLMClient` can successfully route requests to three different, configurable model tiers.
2.  The database schema is fully relational, and a new integration test proves that a task can be created with a `parent_task_id`.
3.  The `personas` table is system-versioned, and a test demonstrates the ability to query a past version of a persona.
4.  The `RunAnalystTier` use case correctly performs the RAG process, verified by new unit tests.
