# 🔱 Praxis: The Mandate of Synthesis

## I. Objective

To fully implement the `RunDirectorTier` use case. This mission will activate the second tier of the adversarial council, creating an agent that can consume multiple, competing Analyst reports, synthesize them into a single, coherent executive briefing, and persist that briefing to the database.

## II. Justification

This mission is the direct successor to the "Mandate of First Light" and represents the first true act of adversarial synthesis in the CHORUS engine. While the Analyst Tier provides breadth, the Director Tier provides judgment and distillation, a critical step in transforming raw analysis into actionable insight. This capability is the core prerequisite for the final Judge Tier.

## III. The Ground Truth (The Current State)

1.  **Functional Analyst Tier:** The "Mandate of First Light" was a success. The `RunAnalystTier` use case is now reliably populating the `analyst_reports` table with structured reports from multiple personas.
2.  **Hollow Use Case:** The `RunDirectorTier` use case exists as a placeholder class but contains no functional logic.
3.  **Empty Archive:** The `director_briefings` table exists in the schema but is never written to.

## IV. The Plan

This mission will be executed in four atomic, verifiable sub-phases.

- **Sub-Phase 1: The Director's Prompt**

  1.  Design the canonical prompt template for the Director persona. This prompt will instruct the LLM to:
      a. Adopt the persona of a senior intelligence director.
      b. Review a provided set of competing reports from subordinate analysts.
      c. Identify the key points of consensus, disagreement, and any underlying, unstated assumptions.
      d. Synthesize these disparate views into a single, balanced, and concise executive briefing.

- **Sub-Phase 2: The Director's Mind (Implementation)**

  1.  Fully implement the `execute` method in `chorus_engine/app/use_cases/run_director_tier.py`.
  2.  This method will first call `self.db.get_analyst_reports` to fetch all reports for the given `query_hash`.
  3.  It will format the collection of reports into the master prompt.
  4.  It will make a call to the **Apex-tier** LLM, as this synthesis of conflicting views is a higher-order reasoning task.
  5.  It will parse the LLM's response to extract the briefing text.

- **Sub-Phase 3: The Director's Hand (Persistence)**

  1.  The `DatabaseInterface` and `PostgresAdapter` already contain the required `save_director_briefing` method. This step is for verification of its suitability.
  2.  The `RunDirectorTier.execute` method will call `self.db.save_director_briefing` to persist its result.

- **Sub-Phase 4: The Verifiable Briefing (The Test)**
  1.  Create a new, focused integration test file: `tests/integration/test_director_produces_briefing.py`.
  2.  This test will be added to a new, isolated test harness (`make test-director`).
  3.  The test will:
      a. Seed the `analyst_reports` table with several distinct, mock reports for a single `query_hash`.
      b. Queue a task and set its status to `PENDING_SYNTHESIS`.
      c. Execute the `RunDirectorTier` use case, providing a mocked LLM that returns a predictable briefing string.
      d. Poll the `director_briefings` table and assert that a new record appears with the correct `query_hash` and briefing text.

## V. Acceptance Criteria

- **AC-1:** The `RunDirectorTier` use case correctly fetches multiple analyst reports from the database.
- **AC-2:** The use case successfully calls the Apex-tier LLM and persists the resulting briefing to the `director_briefings` table.
- **AC-3:** The new `test_director_produces_briefing.py` integration test passes, proving the end-to-end synthesis flow.
- **AC-4:** The full `make test` suite passes, ensuring no regressions have been introduced.
