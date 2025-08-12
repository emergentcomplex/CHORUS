# Idea 01: Implement the Definitive, Three-Tiered LLM Architecture

**1. Concept:**
Evolve the CHORUS engine to a definitive, three-tiered, multi-provider LLM architecture. This will be the foundational model for all AI-driven tasks, optimizing the system for cost, speed, and analytical quality by assigning every task to the appropriate model tier. This architecture, named "The Directorate Standard," reserves our most powerful and expensive reasoning model for the highest-leverage points of synthesis and critique.

**2. Problem Solved:**

- **Architectural Imprecision:** A simple two-tier model lacks the granularity to handle the wide range of tasks in our system, from high-volume data extraction to high-stakes logical deconstruction.
- **Cost/Quality Imbalance:** A two-tier system forces a compromise, either using a costly model for a simple task or a weaker model for a task that demands elite reasoning.
- **Lack of a "Surge" Capability:** The system has no mechanism to deploy its most powerful reasoning capabilities at the most critical moments of judgment.

**3. Proposed Solution:**
This will be implemented by a significant upgrade to the `LLMClient` and a formalization of the model tiers in our configuration and worker logic.

- **A. The Three Tiers:**

  - **Tier 1: Utility Model:** The workhorse for high-volume, low-complexity, and structured-data tasks.
    - **Designated Model (Example):** `xAI Grok-3 Mini`
    - **Tasks:** Collection Plan Generation, "New Knowledge" Assessment, "Pre-Analysis Sieve," Analyst Peer Critiques, Surprise Detection, Query Canonicalization.
  - **Tier 2: Synthesis Model:** The standard for high-quality analysis, nuanced reasoning, and narrative creation.
    - **Designated Model (Example):** `OpenAI o4-mini`
    - **Tasks:** All Analyst-level synthesis and revision passes.
  - **Tier 3: Apex Model:** The elite reasoner for the highest-stakes judgments, logical deconstruction, and meta-cognitive reflection.
    - **Designated Model (Example):** `Anthropic Claude 3 Opus` or a future `GPT-5` class model.
    - **Tasks:** All Director and Judge syntheses, all Devil's Advocate critiques, and the "Living World Model's" amendment proposals.

- **B. Configuration (`.env`):**

  - The `.env` file will be updated to define three distinct roles:
    - `UTILITY_MODEL_PROVIDER` and `UTILITY_MODEL_NAME`
    - `SYNTHESIS_MODEL_PROVIDER` and `SYNTHESIS_MODEL_NAME`
    - `APEX_MODEL_PROVIDER` and `APEX_MODEL_NAME`

- **C. The Upgraded `LLMClient`:**

  - The `LLMClient` will be refactored to manage a pool of clients for all configured providers.
  - Its central `generate_text()` method will now accept a `model_type` of `'utility'`, `'synthesis'`, or `'apex'`.
  - It will route the request to the appropriate provider and model as defined in the `.env` file.
  - The `IntelligentContextPacker` will be updated to be aware of the context limits for all three designated models.

- **D. Worker Refactoring:**
  - All worker scripts will be refactored to call the appropriate model tier for each specific task, as defined in the table above.

**4. Next Steps:**

- This is a **foundational prerequisite for Phase 2 and beyond**. It is the definitive version of our LLM architecture.
- It requires a formal Amendment Proposal to the Constitution to:
  - Replace the "Axiom of Tiered Modeling" with this more detailed, three-tiered definition.
  - Update the "Codebase Architecture" to reflect the new responsibilities of the `LLMClient`.
- The implementation will involve a major refactoring of the `LLMClient` and updates to all worker scripts to specify the correct model tier for their calls.
