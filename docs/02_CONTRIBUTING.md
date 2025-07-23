# 🔱 Contributing to CHORUS

Thank you for your interest in contributing to the CHORUS project. To maintain the quality, consistency, and architectural integrity of the system, we adhere to a strict, axiom-driven development process.

## The Guiding Principles

Before making any changes, you must familiarize yourself with the two foundational documents of this project:

1.  **The Mission Charter (`/docs/00_MISSION_CHARTER.md`):** This document outlines the high-level mission, features, and setup instructions for the project. Ensure any proposed change aligns with this mission.

2.  **The Constitution (`/docs/01_CONSTITUTION.md`):** This is the canonical source of truth for the system's design. It contains the **21 Axioms of CHORUS Development**, the Triumvirate architecture, and the quantitative quality targets we are working towards. **All contributions will be judged against the principles in this document.**

## The Development Workflow

This project is developed in partnership with a generative AI assistant. To ensure consistency, all development sessions **must** be bootstrapped using the official Genesis Prompt.

### Starting a New Development Session

1.  **Generate the Context:** From the project's root directory, run the context generation script:
    ```bash
    ./scripts/generate_context.sh
    ```
    This will create a file named `CONTEXT_FOR_AI.txt` in the project root.

2.  **Start a New Conversation:** Open a new conversation with the designated LLM.

3.  **Provide the Genesis Context:** Copy the *entire contents* of `CONTEXT_FOR_AI.txt` and paste it as the very first prompt in the new conversation.

4.  **Await Confirmation:** The AI should respond with: *"Understood. The CHORUS Genesis context is loaded. I am ready to proceed."*

### Common Development Tasks

All common development tasks are managed through the **CHORUS Command Center**. Use the `Makefile` in the project root for a simplified workflow.

-   To run the full test suite: `make test`
-   To reset and repopulate your local database: `make db-reset && make db-populate`
-   To start all services for manual testing: `make run`

### Proposing Changes

For any architectural changes, you must follow the **Amendment Process** outlined in Part 8 of the Constitution. This involves creating a formal proposal within your pull request.