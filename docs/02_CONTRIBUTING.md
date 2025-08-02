# 🔱 Contributing to CHORUS

Thank you for your interest in contributing to the CHORUS project. To maintain the quality, consistency, and architectural integrity of the system, we adhere to a strict, axiom-driven development process.

## The Guiding Principles

Before making any changes, you must familiarize yourself with the three foundational documents of this project, all located in this `/docs` directory:

1.  **The Mission Charter (`./00_MISSION_CHARTER.md`):** This document outlines the high-level mission, features, and setup instructions for the project. Ensure any proposed change aligns with this mission.

2.  **The Constitution (`./01_CONSTITUTION.md`):** This is the canonical source of truth for the system's design. It contains the **50 Axioms of CHORUS Development**. All contributions will be judged against the principles in this document.

3.  **The System SLOs (`./03_SYSTEM_SLOS.md`):** This document defines the explicit performance and reliability targets for the system. All code must be written with the goal of meeting or exceeding these objectives.

## The Development Praxis

Our development process is designed to fulfill **Axiom 42: Deliberate Velocity**. We have gone well, so that we may now go fast. The `Makefile` provides two distinct, purpose-built workflows: a **Fast Loop** for rapid, iterative development, and a **Verification Workflow** for ensuring correctness.

### I. The Fast Loop (Your 95% Workflow)

This is the workflow for all day-to-day coding. It is designed for an instant feedback loop.

**To start your work session:**
```bash
# Starts all services in the background with your local code mounted.
make run
```

**To test your code as you work:**
```bash
# Run the full suite of tests against the ALREADY RUNNING system.
# This is your primary, fast-feedback command.
make test-fast
```

**To observe the system:**
```bash
# Tails the aggregated logs from all running services in real-time.
make logs
```

**To end your work session:**
```bash
# Stops and removes all running containers and volumes.
make stop
```

### II. The Slow Loop (The Rebuild Path)

You only need this workflow when you change the foundational environment itself (e.g., editing `pyproject.toml` or the `Dockerfile`).

```bash
# Stops the stack, rebuilds the base Docker image, and restarts in dev mode.
make rebuild
```

### III. The Verification Workflow (For CI/CD)

This is the single, atomic command that a continuous integration server must use. It is slow, hermetic, and guarantees correctness from a clean slate.

```bash
# Builds, starts, sets up, tests, and tears down the entire system.
make test```
