# 🔱 Contributing to CHORUS

Thank you for your interest in contributing to the CHORUS project. To maintain the quality, consistency, and architectural integrity of the system, we adhere to a strict, axiom-driven development process.

## The Guiding Principles

Before making any changes, you must familiarize yourself with the canonical documents of this project, all located in the `/docs` directory. They define our mission, our architecture, and our commitment to verification.

## The Development Praxis

Our development process is designed to fulfill **Axiom 49: Deliberate Velocity**. We have gone well, so that we may now go fast. The `Makefile` provides two distinct, purpose-built workflows.

### I. The Fast Loop (Your 95% Workflow)

This is the workflow for all day-to-day coding. It is designed for an instant feedback loop.

```bash
# 1. Start all services in the background.
make run

# 2. As you make code changes, run the fast test suite.
make test-fast

# 3. View aggregated logs from all services.
make logs
```

### II. The Slow Loop (The Launch Path)

You only need this workflow when you change the foundational environment itself (e.g., editing `pyproject.toml` or the `Dockerfile`).

```bash
# Stops the stack, rebuilds the base Docker image, and restarts fresh.
make launch
```

### III. The Verification Workflow (For CI/CD)

This is the single, atomic command that a continuous integration server must use. It is slow, hermetic, and guarantees correctness from a clean slate.

```bash
# Builds, starts, sets up, tests, and tears down the entire system.
make test
```

## The Mandate of Correction (Bug Fix Protocol)

All bug fixes **MUST** adhere to **Axiom 73: Mandated Regression Testing**. The workflow is non-negotiable:
1.  **Replicate:** Write a new automated test that fails, proving the bug's existence.
2.  **Remediate:** Implement the code changes to fix the bug.
3.  **Verify:** Confirm that the new test and all existing tests now pass.

## Commit Message Hygiene

The clarity of our Git history is a reflection of the clarity of our thought. All commit messages **MUST** adhere to the **Conventional Commits** specification.

The format is: `<type>(<scope>): <subject>`

-   **`<type>`:** Must be one of `feat` (new feature), `fix` (bug fix), `docs` (documentation), `style`, `refactor`, `test`, or `chore` (tooling, build process).
-   **`<scope>` (optional):** The part of the codebase affected (e.g., `(ui)`, `(db)`, `(workflow)`).
-   **`<subject>`:** A concise, imperative-mood description of the change.

**Example:**
```
feat(ui): Add adversarial balance visualizer to report page
```

A detailed explanation of the "why" and "what" should be included in the commit body.