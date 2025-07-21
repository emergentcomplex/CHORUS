# Contributing to CHORUS

Thank you for your interest in contributing to the CHORUS project. To maintain the quality, consistency, and architectural integrity of the system, we adhere to a strict, axiom-driven development process.

## The Guiding Principles

Before making any changes, you must familiarize yourself with the two foundational documents of this project:

1.  **The Mission (`README.md`):** The [main README file](./README.md) outlines the high-level mission, features, and setup instructions for the project. Ensure any proposed change aligns with this mission.

2.  **The Architecture (`/docs/blueprint.md`):** The [Architectural Blueprint](./docs/blueprint.md) is the canonical source of truth for the system's design. It contains the **18 Axioms of CHORUS Development**, the Triumvirate architecture, and the quantitative quality targets we are working towards. **All contributions will be judged against these axioms.**

## The Development Workflow

This project is developed in partnership with a generative AI assistant. The workflow is designed to leverage the AI for implementation while maintaining strict human architectural oversight.

1.  **Blueprint First:** All new features or major changes must first be proposed and accepted as an update to the `/docs/blueprint.md`. We do not write code until the plan is codified.

2.  **Test-Driven Development:** All new components (e.g., harvesters) must be accompanied by a corresponding test suite. The tests must validate not only the functional correctness but also the component's adherence to the system's **Service-Level Objectives (SLOs)** as defined in the blueprint.

3.  **Atomic Commits:** Commits should be small, logical, and focused on a single feature or fix. Commit messages should be clear and concise.

4.  **Pull Requests:** All changes should be submitted via a pull request from a feature branch. The description of the pull request should reference which part of the blueprint it is implementing.

By adhering to this process, we ensure that the CHORUS engine remains robust, scalable, and true to its core mission.
