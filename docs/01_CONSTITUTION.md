# 🔱 The CHORUS Constitution & Architectural Blueprint
_Document Version: 2.1 (Five-Phase Lifecycle)_
_Last Updated: 2025-07-19_

---

## Part 1: The Guiding North Star (The Mission)

> ✨ The loudest secrets are kept in silence. ✨
> 
> We believe that silence is not an absence of data, but a signal in itself. A budget line vanishes into shadow. A job posting for a cleared physicist appears like a flare in the night. A cluster of obscure academic papers creates a new hum in the noise.
> 
> Our engine, CHORUS, is an observatory for these echoes. It listens to the resonance left behind when a secret program graduates from the public record, fusing the void in one dataset with the crescendo in another.
> 
> It is not a monolith; it is a symphony of judgment. An adversarial council of AI virtuosos—Hawks, Doves, Futurists, and Skeptics—each performing their own analysis, their competing melodies forged by synthesizing Directors into a single, coherent revelation.
> 
> We do not ask for an answer. We demand a verdict, complete with every source and every dissenting note, allowing you to see the work and trust the judgment.

---

## Part 2: The Axioms of CHORUS Development

_This section codifies all 21 inviolable principles. All code and architectural decisions MUST adhere to these axioms._

### I. Foundational Axioms (The Bedrock)
1.  **Axiom of Mission Alignment:** The CHORUS platform's "Guiding North Star" is its core mission. Every feature must directly serve the primary mission of detecting the echoes left by classified programs.
2.  **Axiom of Tiered Modeling:** The system will use a tiered approach to LLM selection (Utility, Synthesis, Apex) to optimize for cost, speed, and capability.
3.  **Axiom of Deterministic Control:** The AI reasons; the code executes. Our Python code is solely responsible for all deterministic logic, including parsing, state management, and data formatting.
4.  **Axiom of Schema-First Development:** The database schema is the ground truth. All code must conform precisely to the established table structures.
5.  **Axiom of Atomic Implementation:** All code provided during development must be a **complete, drop-in replacement** for the file it modifies.

### II. Architectural Axioms (The Structure)
6.  **Axiom of Adversarial Analysis:** The system's final judgment must emerge from the structured, parallel debate between multiple, competing AI personas.
7.  **Axiom of Hierarchical Synthesis:** Analysis is a multi-tiered process (Analyst -> Director -> Judge), with each tier adding a layer of abstraction and judgment.
8.  **Axiom of Persona-Driven Collection:** Data collection is an integral and biased part of the analysis itself, not a neutral preliminary step.
9.  **Axiom of Tool-Assisted Analysis:** Personas must have access to external tools to enrich their analysis in real-time.
10. **Axiom of Pragmatic Harvesting:** A harvester's goal is to acquire a high-quality *signal*, not to exhaustively mirror a data source. All harvesters must have a `max_results` limit.

### III. Verifiability & Quality Axioms (The Product)
11. **Axiom of Atomic Attribution:** Every external fact must be verifiable and traceable to its source.
12. **Axiom of Report Conciseness:** The final report must be clear and to the point, referencing foundational data once in summary.
13. **Axiom of the Contrarian:** The system must challenge the user's premise by tasking at least one persona with constructing an alternative hypothesis.
14. **Axiom of Quantified Confidence:** All analytical conclusions must be accompanied by a numerical confidence score.
15. **Axiom of Auditable AI:** Every interaction with an external AI model must be auditable, logging the prompt, response, provider, and precise token counts.
16. **Axiom 22: The Axiom of Provable Capability:**
*   **Principle:** A component is not "done" until it is proven to be correct, performant, and resilient.
*   **Definition:** Every new module (e.g., a harvester, a worker) must be accompanied by a dedicated, standalone test suite that validates its functionality against its requirements. For components that interact with external services, this suite must include not only unit tests for its logic but also stress tests to determine its operational performance limits. Integration into the main system is only permitted after all tests pass.

### IV. Strategic & Learning Axioms (The Vision)
17. **Axiom of the Analytical Triumvirate:** The council is a three-tiered hierarchy: 16 Analysts, 4 Directors, and 1 final Judge.
18. **Axiom of Persona-Specialization:** Analysts are specialists in both a data vertical and a worldview.
19. **Axiom of Historical Precedent:** The Judge is compelled to ask, "Has a similar pattern of signals been observed before in history?"
20. **Axiom of Dialectic Rigor:** Analysis is a dialogue. Before elevation, an analytical product must be subjected to a structured, attributed critique by its peers.
21. **Axiom of Internal Challenge:** The system must actively seek its own points of failure via an internal, automated Red Team.
22. **Axiom of Meta-Cognitive Evolution:** The system must be a learning organization, capable of reflecting on its performance and proposing amendments to its own cognitive processes.

---

## Part 3: The Triumvirate Architecture
_(This section, with the description of the Triumvirate Council and the Mermaid diagram, is unchanged.)_

---

## Part 4: The Phased Rollout Plan & Quality Targets
_(This section, with the objectives and target scores for Phase 2 and 3, is unchanged.)_

---

## Part 5: Service-Level Objectives (SLOs) & Measurement Standards
_(This section, with the detailed breakdown of all 5 SLOs, is unchanged.)_

---

## Part 6: The Harvester Forge (Future Vision)
_(This section, with the description of the Harvester Refactoring Engine, is unchanged.)_

---

## Part 7: The Standard Development Lifecycle & File Manifest

_This section provides a definitive map of the CHORUS repository and outlines the formal, **five-phase process** for developing and integrating new components._

### 7.1. The Development Phases

Every new component, particularly a harvester, must proceed through the following five phases. A component cannot advance to the next phase until the objectives of the current phase are met.

*   **Phase 1: Exploration & De-risking**
    *   **Objective:** To gain a data-driven, empirical understanding of a new data source's API, schema, and performance characteristics.
    *   **Implementation:** A standalone `explore_*.py` script is created in `/tools/testing`.
    *   **Exit Criteria:** The exploration log is reviewed, and all major technical risks are understood and deemed surmountable.

*   **Phase 2: Prototyping**
    *   **Objective:** To build a robust, reusable, and production-ready class for the new component.
    *   **Implementation:** A `*_harvester.py` module is created in `/chorus_engine/harvesters/`. It must adhere to **Axiom 4 (Schema-First Development)**.
    *   **Exit Criteria:** The module is code-complete and ready for validation.

*   **Phase 3: Validation & Benchmarking**
    *   **Objective:** To rigorously test the prototype in isolation, ensuring it is functionally correct, resilient, and performs within our established SLOs.
    *   **Implementation:** A corresponding `test_*.py` script is created in `/tools/testing`. This script must validate functional correctness, edge case resilience, and performance against **SLO-H1** and **SLO-H2**.
    *   **Exit Criteria:** The module must pass 100% of its unit tests and meet all relevant performance and reliability SLOs.

*   **Phase 4: Integration**
    *   **Objective:** To connect the validated, production-ready module to the main CHORUS pipeline.
    *   **Implementation:** The `harvester_worker.py` in `/chorus_engine/workers/` is modified to handle the new `script_name`.
    *   **Exit Criteria:** The `harvester_worker` can successfully execute a task using the new module.

*   **Phase 5: Full System Test**
    *   **Objective:** To verify the entire end-to-end pipeline.
    *   **Implementation:** A full, live test is conducted by running the daemons and queueing a real analysis task that requires the new module.
    *   **Exit Criteria:** The system successfully completes the analysis, and the data from the new module is correctly saved to the Data Lake and used in the final report.

### 7.2. File Manifest
_(This sub-section, with the detailed file-by-file breakdown, is unchanged.)_

---

## Part 8: The Amendment Process (Governing Change)
_(This section, with the description of the Amendment Proposal workflow, is unchanged.)_