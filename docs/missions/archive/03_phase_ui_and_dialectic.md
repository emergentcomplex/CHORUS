# Praxis: The Stage (Phase 3)

### Objective
To implement the "Dialectic Chamber" and the "Office of the Devil's Advocate," transforming the analysis into a true adversarial dialogue. We will then build a theatrical UI to visually represent this newly rigorous process.

### Justification
This phase combines the original "Stage" plan with the cognitive architecture from our prior ideas (`Idea 04`, `Idea 06`, `Idea 07`). A polished UI is meaningless if the process it represents is superficial. This phase first deepens the analytical rigor by implementing peer review and red teaming, and *then* builds the masterful UI to showcase it.

### The Plan

*   **Subphase 3.1 (The Chain of Justification):**
    *   **Task:** Upgrade the analytical outputs to include explicit, auditable methods and sources (`Idea 04`).
    *   **Implementation:** The `final_brief` JSON object produced by Analysts will be enriched with a `"methods"` key, detailing the RAG queries and collection plan used. The Director's prompt will be upgraded to synthesize these methods, not just the conclusions.
    *   **File(s) to Modify:** `persona_worker.py`, `director_worker.py`.

*   **Subphase 3.2 (The Dialectic Chamber):**
    *   **Task:** Implement the mandatory, attributed peer review process for Analysts (`Idea 06`).
    *   **Implementation:** The `director_worker` will be upgraded to act as a "Debate Manager." After the initial draft phase, it will spawn 12 "critique" tasks, collect the results, and pass them back to the original Analysts for a final "revision" pass before completing.
    *   **File(s) to Modify:** `director_worker.py`, `persona_worker.py`.

*   **Subphase 3.3 (The Office of the Devil's Advocate):**
    *   **Task:** Embed a formal, multi-stage Red Team to challenge both Directors and the final Judge (`Idea 07`).
    *   **Implementation:** The `director_worker` and `judge_worker` will be modified. After producing a draft synthesis, they will spawn a "Devil's Advocate" task (using the Apex model) to find the biggest logical flaw. They will then perform a final revision step to incorporate the critique.
    *   **File(s) to Modify:** `director_worker.py`, `judge_worker.py`.

*   **Subphase 3.4 (The Verdict Dossier & Visualizer):**
    *   **Task:** Redesign the UI to present the results of this new, deeper process.
    *   **Implementation:** The report page will be redesigned to feature the final verdict, with the full, multi-layered debate (Analyst drafts, peer critiques, Director revisions, Red Team challenges) available in a collapsible "View Council Deliberations" section. A new radar chart will be implemented to visualize the adversarial balance.
    *   **File(s) to Modify:** `chorus_engine/infrastructure/web/templates/details.html`, `chorus_engine/infrastructure/web/web_ui.py`.

### Definition of Done
1.  The JSON output of an Analyst task now contains the "methods" section.
2.  The Director's log shows that it is managing the 12-step critique and revision process.
3.  The Judge's log shows that it is invoking the Devil's Advocate and performing a final revision.
4.  The UI correctly displays the final verdict and the full, auditable debate in their respective sections.
