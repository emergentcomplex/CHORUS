# docs/02_CONTRIBUTING.md

# 🔱 Contributing to CHORUS

Thank you for your interest in contributing to the CHORUS project. To maintain the quality, consistency, and architectural integrity of the system, we adhere to a strict, axiom-driven development process.

## The Guiding Principles

Before making any changes, you must familiarize yourself with the two foundational documents of this project:

1.  **The Mission (`README.md`):** The [main README file](./README.md) outlines the high-level mission, features, and setup instructions for the project. Ensure any proposed change aligns with this mission.

2.  **The Architecture (`/docs/blueprint.md`):** The [Architectural Blueprint](./docs/blueprint.md) is the canonical source of truth for the system's design. It contains the **18 Axioms of CHORUS Development**, the Triumvirate architecture, and the quantitative quality targets we are working towards. **All contributions will be judged against these axioms.**

## The Development Workflow

This project is developed in partnership with a generative AI assistant. To ensure consistency and adherence to our axioms, all development sessions **must** be bootstrapped using the official Genesis Prompt.

### Starting a New Development Session

1.  **Generate the Context:** From the project's root directory, run the context generation script:

    ```bash
    ./scripts/generate_context.sh
    ```

    This will create a file named `CONTEXT_FOR_AI.txt` in the project root. This file is ignored by Git.

2.  **Start a New Conversation:** Open a new conversation with the designated LLM (Gemini 2.5 Pro).

3.  **Provide the Genesis Context:** Copy the _entire contents_ of `CONTEXT_FOR_AI.txt` and paste it as the very first prompt in the new conversation.

4.  **Await Confirmation:** The AI should respond with: _"Understood. The CHORUS Genesis context is loaded. I am ready to proceed."_

5.  **Begin Development:** You can now proceed with the development tasks, confident that the AI is fully aligned with the project's architecture, axioms, and current state.

By adhering to this process, we ensure that the CHORUS engine remains robust, scalable, and true to its core mission.
