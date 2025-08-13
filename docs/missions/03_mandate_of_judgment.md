# 🔱 Praxis: The Mandate of Judgment

## I. Objective

To fully implement the `RunJudgeTier` use case, completing the three-tiered adversarial council. This mission will create the final agent, which consumes the Director's synthesized briefing and renders the definitive, structured verdict, persisting it as the final state of the analysis.

## II. Justification

This mission is the culmination of the core architectural vision. It delivers the final, user-facing product of the CHORUS engine's reasoning process. By transforming the Director's narrative briefing into a structured, machine-readable format, it makes the system's output actionable and auditable. The completion of this mission marks the achievement of a fully functional, end-to-end, multi-tier reasoning pipeline.

## III. The Ground Truth (The Current State)

1.  **Functional Synthesis Tier:** The "Mandate of Synthesis" was a success. The `RunDirectorTier` use case is now reliably populating the `director_briefings` table with synthesized executive briefings.
2.  **Hollow Use Case:** The `RunJudgeTier` use case exists as a placeholder class but contains no functional logic.
3.  **Unused State Table:** The `query_state` table exists but is not yet being used to store the final, structured verdict of a completed analysis.

## IV. The Plan

This mission will be executed in four atomic, verifiable sub-phases.

- **Sub-Phase 1: The Judge's Prompt**

  1.  Design the canonical prompt template for the Judge persona. This prompt will instruct the LLM to:
      a. Adopt the persona of a final arbiter of intelligence.
      b. Review the Director's executive briefing.
      c. Deconstruct the briefing into a structured JSON object containing a final narrative, an argument map, a list of identified intelligence gaps, and a final confidence score.
      d. Ensure the output is **only** the raw JSON object, with no conversational wrapper.

- **Sub-Phase 2: The Judge's Mind (Implementation)**

  1.  Fully implement the `execute` method in `chorus_engine/app/use_cases/run_judge_tier.py`.
  2.  This method will call `self.db.get_director_briefing` to fetch the input for the given `query_hash`.
  3.  It will format the briefing into the master prompt.
  4.  It will make a call to the **Apex-tier** LLM, instructing it to return a JSON object.
  5.  It will parse and validate the JSON response from the LLM.

- **Sub-Phase 3: The Judge's Verdict (Persistence)**

  1.  Add a new abstract method, `save_final_verdict`, to the `DatabaseInterface`.
  2.  Implement the `save_final_verdict` method in the `PostgresAdapter`. This method will take a `query_hash` and a JSON object and execute an `INSERT` or `UPDATE` into the `query_state` table.
  3.  The `RunJudgeTier.execute` method will call this new adapter method to persist the final structured verdict.

- **Sub-Phase 4: The Verifiable Verdict (The Test)**
  1.  Create a new, focused integration test file: `tests/integration/test_judge_produces_verdict.py`.
  2.  This test will be added to a new, isolated test harness (`make test-judge`).
  3.  The test will:
      a. Seed the `director_briefings` table with a mock briefing.
      b. Queue a task and set its status to `PENDING_JUDGMENT`.
      c. Execute the `RunJudgeTier` use case, providing a mocked LLM that returns a predictable, structured JSON string.
      d. Poll the `query_state` table and assert that a new record appears containing the correct, parsed JSON data.

## V. Acceptance Criteria

- **AC-1:** The `DatabaseInterface` and `PostgresAdapter` are updated with the `save_final_verdict` method.
- **AC-2:** The `RunJudgeTier` use case correctly fetches the director's briefing and persists the final structured JSON verdict to the `query_state` table.
- **AC-3:** The new `test_judge_produces_verdict.py` integration test passes, proving the end-to-end judgment flow.
- **AC-4:** The full `make test` suite passes, ensuring the system is holistically stable.
