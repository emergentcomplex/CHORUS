# Praxis: The Echo Chamber (Phase 4)

### Objective
To close the loop and transform the council from a static set of agents into a dynamic, learning organization that can evolve its own cognition, correct its own flaws, and become temporally self-aware.

### Justification
This phase combines the original "Echo Chamber" plan with the advanced cognitive architectures from our prior ideas (`Idea 05`, `Idea 08`, `Idea 11`). A system that cannot learn from its mistakes is doomed to repeat them. This phase implements the core mechanisms for systemic, long-term learning and self-improvement.

### The Plan

*   **Subphase 4.1 (The Bounded Recursive Analyst):**
    *   **Task:** Evolve the Analyst from a single-pass agent into a recursive agent capable of self-correction (`Idea 05`).
    *   **Implementation:** The `persona_worker` will be wrapped in a new "cognitive loop" with deterministic bounds (`MAX_RECURSION_DEPTH`, `NEW_KNOWLEDGE_THRESHOLD`). The agent will now be able to analyze a topic, identify its own intelligence gaps, and recursively launch new, targeted harvesting cycles to fill them.
    *   **File(s) to Modify:** `persona_worker.py`.

*   **Subphase 4.2 (The Living World Model):**
    *   **Task:** Implement the `meta_cognition_daemon` to enable dynamic persona evolution (`Idea 08`).
    *   **Implementation:** A new `meta_cognition_daemon.py` will be created. On a weekly cycle, it will analyze system performance and qualitative "surprises" to propose targeted, evidence-based amendments to the personas' core axioms, using the Apex model. Proposals will be submitted as GitHub Issues for human review.
    *   **File(s) to Create:** `meta_cognition_daemon.py`.

*   **Subphase 4.3 (Temporal Meta-Cognition):**
    *   **Task:** Make the agents temporally self-aware using the system-versioned `personas` table (`Idea 11`).
    *   **Implementation:**
        1.  **Reproducibility:** The `persona_worker` will be upgraded to fetch the version of its persona active at the time the analysis session was created.
        2.  **Cognitive A/B Testing:** The `meta_cognition_daemon` will be enhanced to automatically run A/B tests on proposed persona changes, posting the quantitative results to the GitHub issue.
        3.  **Forensics:** A new `tools/diagnostics/forensic_analyst.py` tool will be created to perform a meta-analysis on failed runs, determining if a specific cognitive change was the likely root cause.
    *   **File(s) to Modify:** `persona_worker.py`, `meta_cognition_daemon.py`.
    *   **File(s) to Create:** `tools/diagnostics/forensic_analyst.py`.

### Definition of Done
1.  A new integration test proves that an Analyst can perform at least one recursive loop to refine its analysis.
2.  The `meta_cognition_daemon` successfully runs and creates a well-formed persona amendment proposal as a GitHub Issue.
3.  The forensic analyst tool can be run against a failed task and produce a plausible root cause analysis.
