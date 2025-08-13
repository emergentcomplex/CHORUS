# 🔱 The Mission Planning Guide

This document outlines the standard operating procedures for executing a development mission with the CHORUS AI.

## Standard Mission Workflow

1.  **Define the Praxis:** A new mission begins by creating a clear, verifiable, step-by-step plan. This plan is codified in a markdown file within `docs/missions/`.
2.  **Generate the Context:** The master context generation script is invoked to create the `CONTEXT_FOR_AI.txt` file. This script dynamically assembles the context based on the mission's needs, typically designating one component as "hot" (full source) and the rest as "cold" (abstracts).
3.  **Initiate the Session:** The session with the AI begins, using the generated context and the Praxis as the primary inputs.
4.  **Execute and Verify:** The AI generates code and commands, which are executed by the operator. The `make test` command is used frequently to verify integrity.
5.  **Commit and Conclude:** Once all acceptance criteria in the Praxis are met and `make test` passes, the changes are committed, and the mission is concluded.

---

## The Dynamic Refactoring Workflow

With the introduction of the "Living Architecture," the mission workflow now includes interactive commands that the AI can issue to the operator. This enables on-the-fly context loading and architectural refactoring.

### The Command & Control Interface (C2I)

The AI communicates its need to use a tool by emitting a formal directive in the following format:
`[DIRECTIVE: COMMAND_NAME(param1="value1", param2="value2")]`

The operator is responsible for translating this directive into the appropriate shell command.

### Workflow 1: On-the-Fly Context Injection

This workflow is used when the AI needs to inspect the source code of a component that was loaded as an abstract.

1.  **AI Action:** Emits `[DIRECTIVE: LOAD_COMPONENT_SOURCE(component="<ComponentName>")]`.
2.  **Operator Action:**
    a. Executes the corresponding script: `./tools/context/load_component.sh <ComponentName>`
    b. Copies the entire output (the purified source code).
    c. Pastes the output into the next prompt for the AI.

### Workflow 2: Architectural Refactoring

This workflow is used when the AI determines the component architecture itself needs to be modified.

1.  **AI Action:** Emits a refactoring directive, such as `[DIRECTIVE: MIGRATE_FILE(file="path/to/file.py", from="OldComponent", to="NewComponent")]`.
2.  **Operator Action:**
    a. Executes the corresponding command: `python3 tools/architecture/refactor.py --migrate-file path/to/file.py --from OldComponent --to NewComponent`
    b. Verifies the script ran successfully and modified `docs/components.json`.
    c. **Crucially, runs the full test suite (`make test`)** to ensure the architectural change has not violated any system invariants.
    d. Commits the changes to `docs/components.json` and any related abstract files.
    e. Regenerates the AI context using the standard `generate_context.sh` script for the next turn.
