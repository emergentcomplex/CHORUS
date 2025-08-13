# 🔱 Praxis: The Mandate of First Light

## I. Objective

To fully implement the `_run_single_analyst_pipeline` method within the `RunAnalystTier` use case. This mission will transform the Analyst from a passive data retriever into an active reasoning agent that consumes Retrieval-Augmented Generation (RAG) context, synthesizes it according to its persona, and saves a structured, verifiable report to the `analyst_reports` table.

## II. Justification

This is the most critical next step in the Master Plan. It builds directly upon the stable foundation of the "Mandate of the Oracle" and delivers the first tangible, end-to-end analytical output of the CHORUS engine. All higher-level missions—including Director-level synthesis, dialectic debate, and final judgment—are blocked until this fundamental capability is proven. This mission makes the engine _work_.

## III. The Ground Truth (The Current State)

1.  **Stable RAG Ingestion:** The "Mandate of the Oracle" was a success. The `chorus-vectorizer` daemon is correctly populating the `semantic_vectors` table with time-encoded vector embeddings.
2.  **Hollow Use Case:** The `RunAnalystTier` use case is a functional shell. It correctly fetches a task and manages state transitions, but its core `_run_single_analyst_pipeline` method is a placeholder that performs no actual reasoning or persistence of its analytical product.
3.  **Empty Archive:** The `analyst_reports` table exists in the schema but is never written to.

## IV. The Plan

This mission will be executed in four atomic, verifiable sub-phases.

- **Sub-Phase 1: The Analyst's Prompt**

  1.  Design the canonical prompt template for the Analyst persona. This prompt will be a multi-part instruction that commands the LLM to:
      a. Adopt a specific persona (e.g., "The Operator," "The Futurist").
      b. Review a provided body of RAG context.
      c. Synthesize the context through the lens of its persona.
      d. Generate a structured report in a specified format (e.g., Markdown with clear headings for Title, Summary, and Findings).

- **Sub-Phase 2: The Analyst's Mind (Implementation)**

  1.  Fully implement the `_run_single_analyst_pipeline` method in `chorus_engine/app/use_cases/run_analyst_tier.py`.
  2.  This method will retrieve the RAG context by calling `self.vector_db.query_similar_documents`.
  3.  It will format the persona's instructions and the retrieved context into the master prompt.
  4.  It will make a call to the `synthesis`-tier LLM (`self.llm.instruct(...)`).
  5.  It will perform basic parsing on the LLM's response to extract the report text.

- **Sub-Phase 3: The Analyst's Hand (Persistence)**

  1.  Add a new abstract method, `save_analyst_report`, to the `DatabaseInterface` in `chorus_engine/app/interfaces.py`.
  2.  Implement the `save_analyst_report` method in the `PostgresAdapter` (`chorus_engine/adapters/persistence/postgres_adapter.py`). This method will take a `query_hash`, `persona_id`, and `report_text` and execute an `INSERT` into the `analyst_reports` table.
  3.  The `_run_single_analyst_pipeline` method will call this new adapter method to persist its result.

- **Sub-Phase 4: The Verifiable Report (The Test)**
  1.  Create a new, focused integration test file: `tests/integration/test_analyst_produces_report.py`.
  2.  This test will be added to a new, isolated test harness (`make test-analyst`) for rapid iteration.
  3.  The test will:
      a. Seed the `semantic_vectors` table with a known document.
      b. Queue a new task in the `task_queue`.
      c. Execute the `RunAnalystTier` use case, providing a mocked LLM that returns a predictable, structured report string.
      d. Poll the `analyst_reports` table and assert that a new record appears with the correct `query_hash`, `persona_id`, and the report text from the mock LLM.

## V. Acceptance Criteria

- **AC-1:** The `DatabaseInterface` is updated with the `save_analyst_report` method.
- **AC-2:** The `PostgresAdapter` correctly implements the `save_analyst_report` method.
- **AC-3:** The `RunAnalystTier` use case successfully calls the LLM and persists the resulting report to the database via the adapter.
- **AC-4:** The new `test_analyst_produces_report.py` integration test passes, proving the end-to-end flow.
- **AC-5:** The full `make test` suite passes, ensuring no regressions have been introduced.
