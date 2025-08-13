# 🔱 Praxis: The Mandate of First Light (v2, Amended)

## I. Objective

To fully implement the `_run_single_analyst_pipeline` method within the `RunAnalystTier` use case. This mission will transform the Analyst into an active reasoning agent that consumes RAG context, synthesizes it according to its persona, and saves a structured report. Critically, this mission will also establish the **Chain of Justification** by persisting the methods and sources used by the Analyst, making all reasoning auditable from the very first step.

## II. Justification

This is the most critical next step in the Master Plan. It delivers the first tangible analytical output of the CHORUS engine. By integrating the "Chain of Justification" at this foundational stage, we ensure that our core principle of auditable, evidence-based reasoning is baked into the system's DNA, not added as an afterthought. This mission makes the engine _work_, and it makes it _trustworthy_.

## III. Guiding Precepts & Inviolable Constraints

**A. The Mandate of Tiered Cognition:** This mission will be the first to implement the three-tiered LLM architecture. The `RunAnalystTier` use case **MUST** be engineered to use a formal `LLMClient` capable of directing tasks to the appropriate model tier (e.g., using the `synthesis`-tier model for its primary report generation).

## IV. The Ground Truth (The Current State)

1.  **Stable RAG Ingestion:** The `chorus-vectorizer` daemon is correctly populating the `semantic_vectors` table.
2.  **Hollow Use Case:** The `RunAnalystTier` use case is a functional shell.
3.  **Incomplete Schema:** The `analyst_reports` table lacks a column to store the Chain of Justification.

## V. The Plan

- **Sub-Phase 1: The Analyst's Prompt**

  1.  Design the canonical prompt template for the Analyst persona. This prompt will instruct the LLM to generate a structured report **and** to output a machine-readable summary of the methods it used to arrive at its conclusions.

- **Sub-Phase 2: The Analyst's Mind (Implementation)**

  1.  Fully implement the `_run_single_analyst_pipeline` method in `run_analyst_tier.py`.
  2.  It will retrieve RAG context via `self.vector_db.query_similar_documents`.
  3.  It will make a call to the `synthesis`-tier LLM.
  4.  It will parse the LLM's response to extract both the report text and the structured **"methods" data (the Chain of Justification)**.

- **Sub-Phase 3: The Analyst's Hand (Persistence)**

  1.  **Amend Schema:** Modify `infrastructure/postgres/init.sql` to add a `methods_used JSONB` column to the `analyst_reports` table.
  2.  **Amend Interface:** Add the `methods_data: dict` parameter to the `save_analyst_report` method in the `DatabaseInterface`.
  3.  **Amend Adapter:** Implement the updated `save_analyst_report` method in the `PostgresAdapter` to persist both the report text and the JSONB methods data.
  4.  The `_run_single_analyst_pipeline` method will call this new adapter method.

- **Sub-Phase 4: The Verifiable Report (The Test)**
  1.  Create a new, focused integration test: `tests/integration/test_analyst_produces_report.py`.
  2.  The test will:
      a. Seed the `semantic_vectors` table.
      b. Queue a task.
      c. Execute the `RunAnalystTier` use case with a mocked LLM that returns a predictable report and methods block.
      d. Poll the `analyst_reports` table and assert that the new record contains the correct report text **and** that the `methods_used` column is correctly populated.

## VI. Acceptance Criteria

- **AC-1:** The `analyst_reports` table is amended with a `methods_used JSONB` column.
- **AC-2:** The `DatabaseInterface` and `PostgresAdapter` are updated to handle the persistence of the methods data.
- **AC-3:** The `RunAnalystTier` use case is implemented using the tiered `LLMClient` and correctly saves both the report and its Chain of Justification.
- **AC-4:** The new `test_analyst_produces_report.py` integration test passes.
- **AC-5:** The full `make test` suite passes.
