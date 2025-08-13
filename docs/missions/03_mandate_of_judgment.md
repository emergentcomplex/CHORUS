# 🔱 Praxis: The Mandate of Judgment (v2, Amended)

## I. Objective

To fully implement the `RunJudgeTier` use case, completing the three-tiered adversarial council. This mission will create the final agent, which consumes the Director's synthesized, meta-analytical briefing and renders the definitive, structured verdict.

## II. Justification

This mission is the culmination of the core architectural vision. It delivers the final, user-facing product of the CHORUS engine's reasoning process. By transforming the Director's narrative briefing into a structured, machine-readable JSON object, it makes the system's output actionable, auditable, and ready for visualization.

## III. Guiding Precepts & Inviolable Constraints

**A. The Mandate of Tiered Cognition:** The Judge's final deconstruction of a narrative into a structured, logical format is a demanding reasoning task. This mission **MUST** use the **Apex-tier** LLM and instruct it to return a valid JSON object.

## IV. The Ground Truth (The Current State)

1.  **Functional Synthesis Tier:** The `director_briefings` table is being populated with synthesized executive briefings.
2.  **Hollow Use Case:** The `RunJudgeTier` use case is a placeholder.

## V. The Plan

- **Sub-Phase 1: The Judge's Prompt**

  1.  Design the canonical prompt template for the Judge. This prompt will instruct the LLM to:
      a. Adopt the persona of a final arbiter of intelligence.
      b. Review the Director's executive briefing.
      c. Deconstruct the briefing into a structured JSON object containing a final narrative, an argument map, a list of intelligence gaps, and a final confidence score.
      d. Ensure the output is **only** the raw JSON object.

- **Sub-Phase 2: The Judge's Mind (Implementation)**

  1.  Fully implement the `execute` method in `run_judge_tier.py`.
  2.  It will call `self.db.get_director_briefing` to fetch the input.
  3.  It will format the briefing into the master prompt.
  4.  It will make a call to the **Apex-tier** LLM, instructing it to return a JSON object.
  5.  It will parse and validate the JSON response.

- **Sub-Phase 3: The Judge's Verdict (Persistence)**

  1.  Add a new abstract method, `save_final_verdict`, to the `DatabaseInterface`.
  2.  Implement the `save_final_verdict` method in the `PostgresAdapter` to `INSERT` or `UPDATE` the `query_state` table.
  3.  The `RunJudgeTier.execute` method will call this new adapter method.

- **Sub-Phase 4: The Verifiable Verdict (The Test)**
  1.  Create a new integration test: `tests/integration/test_judge_produces_verdict.py`.
  2.  The test will:
      a. Seed the `director_briefings` table with a mock briefing.
      b. Set a task's status to `PENDING_JUDGMENT`.
      c. Execute the `RunJudgeTier` use case with a mocked LLM that returns a predictable, structured JSON string.
      d. Poll the `query_state` table and assert that a new record appears containing the correct, parsed JSON data.

## VI. Acceptance Criteria

- **AC-1:** The `DatabaseInterface` and `PostgresAdapter` are updated with the `save_final_verdict` method.
- **AC-2:** The `RunJudgeTier` use case successfully calls the Apex-tier LLM and persists the final structured JSON verdict.
- **AC-3:** The new `test_judge_produces_verdict.py` integration test passes.
- **AC-4:** The full `make test` suite passes.
