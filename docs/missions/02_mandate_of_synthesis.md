# 🔱 Praxis: The Mandate of Synthesis (v2, Amended)

## I. Objective

To fully implement the `RunDirectorTier` use case. This mission will activate the second tier of the adversarial council, creating an agent that consumes multiple, competing Analyst reports **and their corresponding Chains of Justification**, synthesizes them into a single, coherent executive briefing, and persists that briefing to the database.

## II. Justification

This mission represents the first true act of adversarial synthesis in the CHORUS engine. By engineering the Director to perform a meta-analysis of the Analysts' _methods_ (not just their conclusions), we transform it from a simple summarizer into a true meta-analyst who can judge the _process_ of intelligence gathering. This is a critical step in creating a trustworthy, auditable judgment.

## III. Guiding Precepts & Inviolable Constraints

**A. The Mandate of Tiered Cognition:** The Director's synthesis of conflicting viewpoints and methodologies is a higher-order reasoning task. This mission **MUST** use the **Apex-tier** LLM for its primary synthesis prompt to ensure the highest quality of meta-analytical judgment.

## IV. The Ground Truth (The Current State)

1.  **Functional Analyst Tier:** The `analyst_reports` table is being populated with structured reports and their `methods_used` data.
2.  **Hollow Use Case:** The `RunDirectorTier` use case is a placeholder.

## V. The Plan

- **Sub-Phase 1: The Director's Prompt**

  1.  Design the canonical prompt template for the Director. This prompt will explicitly instruct the LLM to:
      a. Adopt the persona of a senior intelligence director.
      b. Review the provided set of competing Analyst reports **and their `methods_used` data**.
      c. **Explicitly comment on areas of methodological convergence or divergence** between the Analysts.
      d. Synthesize these disparate views and methods into a single, balanced executive briefing that includes an assessment of confidence based on the quality of the underlying analytical work.

- **Sub-Phase 2: The Director's Mind (Implementation)**

  1.  Fully implement the `execute` method in `run_director_tier.py`.
  2.  It will call `self.db.get_analyst_reports` to fetch all data for the `query_hash`.
  3.  It will format the collection of reports and their Chains of Justification into the master prompt.
  4.  It will make a call to the **Apex-tier** LLM.

- **Sub-Phase 3: The Director's Hand (Persistence)**

  1.  The `save_director_briefing` method in the `PostgresAdapter` is sufficient. The `execute` method will call it to persist the result.

- **Sub-Phase 4: The Verifiable Briefing (The Test)**
  1.  Create a new integration test: `tests/integration/test_director_produces_briefing.py`.
  2.  The test will:
      a. Seed the `analyst_reports` table with mock reports, including varied `methods_used` data.
      b. Set a task's status to `PENDING_SYNTHESIS`.
      c. Execute the `RunDirectorTier` use case with a mocked LLM.
      d. Assert that the `director_briefings` table is correctly populated.
      e. **Crucially, assert that the prompt sent to the mock LLM contains the `methods_used` data.**

## VI. Acceptance Criteria

- **AC-1:** The `RunDirectorTier` use case correctly fetches both reports and their `methods_used` data.
- **AC-2:** The Director's prompt explicitly instructs the LLM to perform a meta-analysis of the Analysts' methods.
- **AC-3:** The use case successfully calls the Apex-tier LLM and persists the resulting briefing.
- **AC-4:** The new `test_director_produces_briefing.py` integration test passes.
- **AC-5:** The full `make test` suite passes.
