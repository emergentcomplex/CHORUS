# Idea 08: Implement the "Office of the Devil's Advocate" (Multi-Stage Red Teaming)

**1. Concept:**
Activate the "Devil's Advocate" persona as a formal, automated Red Team that is constitutionally embedded at multiple stages of the synthesis process. Instead of a single, final critique, the Devil's Advocate will be triggered to challenge the work of both the **Directors** and the final **Judge**, ensuring that analytical flaws are caught and addressed before the final report is produced.

**2. Problem Solved:**
- **Single Point of Synthesis Failure:** A single Director could synthesize their four Analyst briefs in a flawed way, allowing a "groupthink" consensus from one directorate to proceed unchallenged to the final Judge.
- **Insufficient Final Scrutiny:** A single Red Team review at the very end of the process is helpful, but it doesn't allow the system to *correct* the identified flaws. It only flags them.

**3. Proposed Solution:**
This will be implemented by integrating a new "Red Team" stage into the `director_worker` and `judge_worker`'s cognitive loops.

- **A. The Directorate-Level Red Team:**
  - After a `director_worker` completes its initial synthesis of the four Analyst briefs, it produces a `draft_directorate_summary`.
  - Before this draft can be sent to the Judge, the `director_worker` will spawn a new, high-priority **"Devil's Advocate" task**.
  - A `persona_worker`, configured with the "Devil's Advocate" persona, will claim this task.
  - **The Scope (per your directive):** The Devil's Advocate will be given the full context available to the Director: the four original Analyst briefs and the Director's draft summary.
  - The prompt will be: "You are an expert in logical fallacies and cognitive biases. Review the four analyst briefs and the director's attempt to synthesize them. Identify the single biggest logical flaw, unstated assumption, or point of groupthink in the director's draft summary." This call uses the **Synthesis Model**.
  - The resulting critique is passed back to the `director_worker`.

- **B. The Director's Revision:**
  - The `director_worker` performs a final "Revision" step, similar to the Analysts in the Dialectic Chamber. It makes one last call to the Synthesis Model with the prompt: "Here is your draft summary and the critique from the Devil's Advocate. Revise your summary to address or rebut this critique and produce your final, more rigorous Directorate Summary."

- **C. The Judge-Level Red Team:**
  - The exact same process is repeated at the next level. The `judge_worker` will synthesize the four *revised* Directorate Summaries into a "Final Draft Report."
  - It will then spawn its own Devil's Advocate task, providing the four Directorate Summaries and its own final draft as context.
  - The Judge will then perform a final revision based on the Devil's Advocate's ultimate critique.

- **D. Final Publication:**
  - The final, twice-red-teamed report is published to the user. The critiques from both the Directorate-level and Judge-level Red Team reviews will be included in the final auditable metadata in the `llm_calls` table.

**4. Next Steps:**
- This is a major upgrade to the rigor of the entire system, best slated for **Phase 3**, as it requires the Director and Judge workers to be functional.
- It requires a formal Amendment Proposal to the Constitution to:
  - Update the "Triumvirate Architecture" to include these two new Red Team review stages.
  - Codify the "Axiom of Internal Challenge" to make this process a core principle.
- The implementation will involve significant new logic in both the `director_worker` and the future `judge_worker`.
