# 🔱 Contributing to CHORUS

Thank you for your interest in contributing to the CHORUS project. To maintain the quality, consistency, and architectural integrity of the system, we adhere to a strict, axiom-driven development process.

## The Guiding Principles

Before making any changes, you must familiarize yourself with the canonical documents of this project. They define our mission, our architecture, and our commitment to verification. The supreme law is [🔱 The Constitution](./00_THE_CONSTITUTION.md).

---

## Quickstart Guide

This guide provides the definitive steps to set up and run the entire CHORUS system locally using `make` and Docker.

### Prerequisites

- **Git:** For cloning the repository.
- **Docker & Docker Compose:** For running the entire containerized environment.

### 1. Initial Setup

```bash
# Clone the repository and navigate into it
git clone <your-repo-url>
cd CHORUS

# Create your personal environment file from the template
cp .env.example .env

# Open .env with your editor and add your GOOGLE_API_KEY
# nano .env
```

### 2. Build and Run the System

This single command builds the Docker images (a one-time slow operation) and starts all services in development mode.

```bash
# This command will stop, build, and start the entire stack.
make rebuild
```

Subsequent starts can use the faster `make run` command.

### 3. Access the System

- **CHORUS C2 UI:** [http://localhost:5001](http://localhost:5001)
- **Redpanda Console (Kafka UI):** [http://localhost:8080](http://localhost:8080)

---

## The Development Praxis

Our development process is designed to fulfill **Axiom 49: Deliberate Velocity**. The `Makefile` provides two distinct, purpose-built workflows.

### I. The Fast Loop (Your 95% Workflow)

This is the workflow for all day-to-day coding. It is designed for an instant feedback loop.

```bash
# 1. Start all services in the background.
make run

# 2. As you make code changes, run the fast test suite.
make test-fast
```

### II. The Verification Workflow (For CI/CD)

This is the single, atomic command that a continuous integration server must use. It is slow, hermetic, and guarantees correctness from a clean slate.

```bash
# Builds, starts, sets up, tests, and tears down the entire system.
make test
```

## The Mandate of Correction (Bug Fix Protocol)

All bug fixes **MUST** adhere to **Axiom 73: Mandated Regression Testing**.

## Commit Message Hygiene

All commit messages **MUST** adhere to the **Conventional Commits** specification.
