# Idea 05: Implement the "Bounded Recursive Analyst" Cognitive Loop

**1. Concept:**
Evolve the `persona_worker` from a linear, single-pass agent into a dynamic, recursive agent capable of self-correction and intelligent, multi-pass analysis. The Analyst will now be able to analyze a topic, identify its own knowledge gaps, and then recursively launch new, more targeted harvesting cycles to fill those gaps until a satisfactory conclusion is reached. This entire process is controlled by a set of deterministic bounds to ensure stability, performance, and efficiency.

**2. Problem Solved:**

- **Superficial Analysis:** A single-pass analysis is entirely dependent on the quality of its initial collection plan. If that plan is too broad or misses a key concept, the final report will be superficial and lack the necessary depth.
- **Lack of Adaptability:** The current model cannot adapt its strategy mid-analysis. It cannot "realize" it's going down the wrong path or that a new, more important line of inquiry has emerged from the initial data.

**3. Proposed Solution:**
This will be implemented as a new, advanced operational mode within the `persona_worker.py` script. It will be a sophisticated "cognitive loop" that wraps the existing Plan -> Harvest -> Synthesize cycle.

- **A. Core Parameters:**

  - `MAX_RECURSION_DEPTH = 3`: A static, integer failsafe.
  - `NEW_KNOWLEDGE_THRESHOLD = 0.25`: A dynamic, quality-based exit condition.

- **B. The Recursive Cognitive Loop:**

  - The `run_analysis_pipeline` method will be wrapped in a `while` loop that checks the two exit conditions.
  - A `guiding_instruction` variable will be used, starting with the user query and then updated with the primary intelligence gap from the previous loop.

- **C. Adaptive Tool Selection:**

  - The Collection Plan Generation prompt will be dynamically updated in each loop with the current `guiding_instruction`. This call will use the **`utility`** model tier for speed and cost-effectiveness (`llm_client.generate_text(..., model_type='utility')`).

- **D. The "New Knowledge" Assessment (The Quality Gate):**

  - After each analysis pass (from depth 1 onwards), the worker will compare the new analysis with the previous one.
  - It will make a single, fast call to the **`utility`** model tier for a semantic comparison task, which returns a `new_knowledge_score` (`llm_client.generate_text(..., model_type='utility', is_json=True)`).

- **E. The Synthesis Step:**
  - The main synthesis at the end of each loop will continue to use the high-quality **`synthesis`** model tier (`llm_client.generate_text(..., model_type='synthesis')`).

**4. Next Steps:**

- This is a major architectural evolution of the Analyst's cognitive model, best slated for **Phase 3**.
- It requires a formal Amendment Proposal to the Constitution to codify the "Axiom of Reflective Analysis."
- The implementation will be a significant refactoring of the `persona_worker.py`'s main execution logic.
