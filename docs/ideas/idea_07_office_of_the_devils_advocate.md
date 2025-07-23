# Idea 07: Implement the "Office of the Devil's Advocate" (Multi-Stage Red Teaming)

**1. Concept:**
Activate the "Devil's Advocate" persona as a formal, automated Red Team that is constitutionally embedded at multiple stages of the synthesis process. The Devil's Advocate will be triggered to challenge the work of both the **Directors** and the final **Judge**, ensuring that analytical flaws are caught and addressed before the final report is produced.

**2. Problem Solved:**

- **Single Point of Synthesis Failure:** A single Director could synthesize their four Analyst briefs in a flawed way, allowing a "groupthink" consensus from one directorate to proceed unchallenged to the final Judge.
- **Insufficient Final Scrutiny:** A single Red Team review at the very end of the process is helpful, but it doesn't allow the system to _correct_ the identified flaws. It only flags them.

**3. Proposed Solution:**
This will be implemented by integrating a new "Red Team" stage into the `director_worker` and `judge_worker`'s cognitive loops.

- **A. The Directorate-Level Red Team:**

  - After a `director_worker` completes its initial synthesis, it produces a `draft_directorate_summary`.
  - It will then spawn a "Devil's Advocate" task.
  - The Devil's Advocate persona will perform its critique. This is a difficult, high-reasoning task that requires the best possible logical deconstruction. Therefore, this call will exclusively use the **`apex`** model tier (`llm_client.generate_text(..., model_type='apex')`).

- **B. The Director's Revision:**

  - The `director_worker` performs a final "Revision" step, using the **`apex`** model tier again to incorporate the Red Team's critique into its final, more rigorous Directorate Summary.

- **C. The Judge-Level Red Team:**
  - The exact same process is repeated at the next level. The `judge_worker` will synthesize the Directorate Summaries, have its draft critiqued by the Devil's Advocate using the **`apex`** model, and then perform its own final revision using the **`apex`** model.

**4. Next Steps:**

- This is a major upgrade to the rigor of the entire system, best slated for **Phase 3**.
- It requires a formal Amendment Proposal to the Constitution to codify the "Axiom of Internal Challenge."
- The implementation will involve significant new logic in both the `director_worker` and the future `judge_worker`.
