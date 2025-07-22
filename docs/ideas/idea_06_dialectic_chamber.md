# Idea 07: Implement the "Dialectic Chamber" (Attributed Peer Review)

**1. Concept:**
Enhance the Analyst tier by introducing a new, mandatory "Debate" phase. Before an Analyst can submit its final brief to its Director, it must first circulate a draft to its three directorate peers for critique and then revise its work based on their attributed feedback. This transforms the analysis from a set of four independent monologues into a true, collaborative-adversarial dialogue.

**2. Problem Solved:**
- **Unchallenged Bias:** In the current model, an Analyst's brief is not challenged until it reaches the Director. This allows flawed or biased reasoning to proceed up the chain without being checked by a peer with a competing worldview.
- **Lack of Cross-Pollination:** Analysts currently work in isolation. The Hawk never benefits from the Dove's perspective on de-escalation, and the Futurist never benefits from the Skeptic's grounding in fiscal reality until it's too late.

**3. Proposed Solution:**
This will be implemented as a new, multi-step "Debate" phase within the `persona_worker`'s execution logic.

- **A. Drafting:** All four Analysts in a directorate complete their initial Plan -> Harvest -> Synthesize cycle, producing a `draft_brief`.

- **B. Circulation & Critique:** A new "Debate Manager" component (likely part of the `director_worker`'s initial logic) will be responsible for this phase.
  - It will collect the four `draft_briefs`.
  - It will then create **12 new, fast, high-priority tasks** for the `trident_launcher`.
  - Each task will be a "critique" task, assigning one Analyst's draft to another Analyst for review. For example: `{"mode": "analyst_critique", "reviewer_persona": "analyst_dove", "draft_to_review": {...}}`.
  - The `persona_worker` will have a new, lightweight execution mode for these tasks. It will make a single call to the **Utility Model** with a prompt like: "You are [Reviewer Persona]. Provide a one-paragraph critique of the following draft from your colleague, the [Original Author Persona], based on your unique worldview."

- **C. Revision:**
  - Once the 12 critique tasks are complete, the Debate Manager will route the three critiques back to each of the original four Analysts.
  - Each `persona_worker` will then be re-activated for a final "Revision" step. It will make one last call to the **Synthesis Model** with a prompt like: "Here is your draft brief and the attributed critiques from your colleagues. Revise your brief to address or rebut these critiques and produce your final, most defensible analysis."

- **D. Final Submission:** The revised brief is then saved as the `final_brief` and the Analyst's task is marked as `COMPLETED`.

**4. Next Steps:**
- This is a major architectural evolution of the Analyst's cognitive process, best slated for **Phase 3**.
- It requires a formal Amendment Proposal to the Constitution to update the "Triumvirate Architecture" to include this new "Debate" phase and to codify the "Axiom of Dialectic Rigor."
- The implementation will involve significant modifications to the `director_worker` (to act as the Debate Manager) and the `persona_worker` (to handle the new "critique" and "revision" modes).
