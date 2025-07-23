# Idea 06: Implement the "Dialectic Chamber" (Attributed Peer Review)

**1. Concept:**
Enhance the Analyst tier by introducing a new, mandatory "Debate" phase. Before an Analyst can submit its final brief to its Director, it must first circulate a draft to its three directorate peers for critique and then revise its work based on their attributed feedback. This transforms the analysis from a set of four independent monologues into a true, collaborative-adversarial dialogue.

**2. Problem Solved:**

- **Unchallenged Bias:** In the current model, an Analyst's brief is not challenged until it reaches the Director. This allows flawed or biased reasoning to proceed up the chain without being checked by a peer with a competing worldview.
- **Lack of Cross-Pollination:** Analysts currently work in isolation. The Hawk never benefits from the Dove's perspective on de-escalation, and the Futurist never benefits from the Skeptic's grounding in fiscal reality until it's too late.

**3. Proposed Solution:**
This will be implemented as a new, multi-step "Debate" phase within the `persona_worker`'s execution logic, orchestrated by the `director_worker`.

- **A. Drafting:** All four Analysts in a directorate complete their initial synthesis using the **`synthesis`** model tier.

- **B. Circulation & Critique:** The `director_worker` will spawn 12 new "critique" tasks.

  - The `persona_worker`, in a lightweight "critique" mode, will make a single call to the fast and cost-effective **`utility`** model tier for each critique (`llm_client.generate_text(..., model_type='utility')`).

- **C. Revision:**
  - Each Analyst receives the three critiques of its work.
  - It then performs a final "Revision" step, making one last call to the high-quality **`synthesis`** model tier to incorporate the feedback and produce its final, most defensible brief (`llm_client.generate_text(..., model_type='synthesis')`).

**4. Next Steps:**

- This is a major architectural evolution of the Analyst's cognitive process, best slated for **Phase 3**.
- It requires a formal Amendment Proposal to the Constitution to codify the "Axiom of Dialectic Rigor."
- The implementation will involve significant modifications to the `director_worker` and `persona_worker`.
