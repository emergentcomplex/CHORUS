# Idea 01 (Revised): Implement the Definitive, Three-Tiered LLM Architecture

**1. Concept:**
Evolve the CHORUS engine to a definitive, three-tiered, multi-provider LLM architecture. This will be the foundational model for all AI-driven tasks, optimizing the system for cost, speed, and analytical quality by assigning every task to the appropriate model tier. This architecture, named "The Directorate Standard," reserves our most powerful and expensive reasoning model for the highest-leverage points of synthesis and critique.

**2. Problem Solved:**

- **Architectural Imprecision:** Our previous "Tiered Model" idea was a good start, but it lacked a precise definition of which tasks belong to which tier.
- **Cost/Quality Imbalance:** A two-tier system forces a compromise, potentially using a costly model for a task that doesn't require it, or a weaker model for a task that demands elite reasoning.
- **Lack of a "Surge" Capability:** The system has no mechanism to deploy its most powerful reasoning capabilities at the most critical moments of judgment.

**3. Proposed Solution:**
This will be implemented by a significant upgrade to the `LLMClient` and a formalization of the model tiers in our configuration and worker logic.

- **A. The Three Tiers:**

  - **Tier 1: Utility Model:** The workhorse for high-volume, low-complexity tasks.
    - **Designated Model (Example):** `xAI Grok-3 Mini`
    - **Tasks:** Collection Plan Generation, "New Knowledge" Assessment, "Pre-Analysis Sieve," Analyst Peer Critiques.
  - **Tier 2: Synthesis Model:** The standard for high-quality analysis and narrative creation.
    - **Designated Model (Example):** `OpenAI o4-mini`
    - **Tasks:** All Analyst-level synthesis and revision passes.
  - **Tier 3: Apex Model:** The elite reasoner for the highest-stakes judgments.
    - **Designated Model (Example):** `Anthropic Claude 3 Opus` or `GPT-5`
    - **Tasks:** All Director and Judge syntheses, and all Devil's Advocate critiques.

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
  - All worker scripts will be refactored to call the appropriate model tier for each specific task, as defined in the table above. For example:
    - The `persona_worker` will call `model_type='utility'` for its planning and `model_type='synthesis'` for its final brief.
    - The `director_worker` will call `model_type='apex'` for its synthesis.
    - The `persona_worker` (in Devil's Advocate mode) will call `model_type='apex'` for its critique.

**4. Next Steps:**

- This is a **foundational prerequisite for Phase 2 and beyond**. It is the definitive version of our LLM architecture.
- It requires a formal Amendment Proposal to the Constitution to:
  - Replace the "Axiom of Tiered Modeling" with this more detailed, three-tiered definition.
  - Update the "Codebase Architecture" to reflect the new responsibilities of the `LLMClient`.
- The implementation will involve a major refactoring of the `LLMClient` and updates to all worker scripts to specify the correct model tier for their calls.
