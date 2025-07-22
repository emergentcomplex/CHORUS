# Idea 01: Implement the Tiered, Multi-Model LLM Architecture

**1. Concept:**
Evolve the CHORUS engine from its current single-model dependency to a sophisticated, multi-provider architecture. This involves creating a tiered system that intelligently routes specific tasks to the most appropriate Large Language Model based on a "right tool for the right job" philosophy. This is the highest priority architectural upgrade required to make the Phase 2 "Chamber Orchestra" both functionally capable and economically viable.

**2. Problem Solved:**
- **Capability Mismatch:** Not all analytical tasks are equal. Using a massive, high-cost synthesis model for simple, high-volume data extraction (like in the ingestion pipeline) is inefficient and wasteful. Conversely, using a small, fast model for the final, complex synthesis of competing Analyst briefs would produce a low-quality, superficial report.
- **Vendor Lock-In & Brittleness:** The current system is hard-coded to a single provider. If that provider has an outage, changes its API, or is not the best-in-class for a specific task, the entire CHORUS engine is compromised.
- **Cost Optimization:** A single-model approach forces us to pay a premium for every single LLM call, even the simple ones. A tiered system allows us to use faster, cheaper models for the majority of high-volume tasks, reserving the expensive, high-capability models for only the most critical reasoning and synthesis steps.

**3. Proposed Solution:**
This will be implemented via a new, definitive `llm_client.py` utility, which will act as a universal, provider-agnostic abstraction layer for the entire system.

- **A. Configuration (`.env`):**
  - The `.env` file will be updated to define two distinct roles:
    - `UTILITY_MODEL_PROVIDER`: The provider for fast, structured data tasks (e.g., `xai`).
    - `SYNTHESIS_MODEL_PROVIDER`: The provider for high-stakes reasoning and report generation (e.g., `openai`).
  - It will also contain the API keys for all supported providers.

- **B. The `LLMClient` Module:**
  - This new module will initialize and manage a pool of clients for all configured providers (OpenAI, xAI, Google, etc.).
  - It will contain a central `generate_text()` method that accepts a new, critical argument: `model_type` (either `'utility'` or `'synthesis'`).
  - Based on the `model_type`, the client will route the request to the appropriate provider and model as defined in the `.env` file.

- **C. The "Intelligent Context Packer":**
  - This will be a sub-component of the `LLMClient`. It will be responsible for all prompt construction and token management.
  - It will use the `tiktoken` library for precise, universal token counting.
  - It will be "provider-aware," fetching the correct context window limit for the designated model (e.g., 200k for `o4-mini`, 128k for `grok-3-mini`).
  - It will implement the **"LLM-Powered Pre-Analysis Sieve"** as its primary strategy for handling context overflow. If a prompt's context is too large, it will make a fast, low-cost call to the `utility` model to intelligently rank and select the most relevant data, which is then passed to the `synthesis` model. This avoids destructive, naive truncation.

- **D. Refactoring of All Worker Scripts:**
  - All scripts that currently make direct LLM calls (`persona_worker.py`, `ingest_*.py`, `ab_test_judger.py`) will be refactored.
  - Their provider-specific logic will be removed and replaced with a single, clean call to the new `llm_client.generate_text(..., model_type='...')` method.

**4. Next Steps:**
- This is a **foundational prerequisite for Phase 2**.
- It requires a formal Amendment Proposal to the Constitution to:
  - Replace the "Axiom of Model Standardization" with the "Axiom of Tiered Modeling."
  - Update the "Codebase Architecture" to include the new `llm_client.py` utility.
- The implementation will involve creating the new `llm_client.py` file and then refactoring all four affected worker scripts to use it.
