# 🔱 Praxis: The Mandate of the Living Architecture (Ratified)

## I. Objective

To create a suite of production-grade tools that enable dynamic, in-session management of the AI's context and the system's component architecture. This involves establishing a formal AI-to-tool communication protocol and building the scripts necessary to load component source code on-demand and to refactor the component architecture itself.

## II. Guiding Precepts & Inviolable Constraints

**A. The Axiom of AI Agency:**
The AI is not merely a passive recipient of context. It must be empowered to request deeper knowledge and propose architectural changes when a mission's requirements demand it.

**B. The Axiom of Atomic Refactoring:**
All architectural changes (migrating files, creating/deleting components) MUST be executed by a robust, validating tool. The tool, not the AI, is responsible for modifying the master component manifest, ensuring its integrity.

**C. The Axiom of Verifiability:**
The `make test` suite remains the ultimate arbiter of system health. Any architectural refactoring must result in a state that passes all verification tests.

## III. The Plan

This mission will be executed by creating two new toolkits: one for managing the AI's immediate context, and one for managing the long-term system architecture.

- **Sub-Phase 1: The AI Command & Control Interface (C2I)**

  1.  **Define the Directive Protocol:** We will establish a formal, machine-parsable syntax that the AI can emit to signal its intent to use a tool. This prevents the AI from having to generate shell commands directly. The format will be:
      `[DIRECTIVE: COMMAND_NAME(param1="value1", param2="value2")]`

- **Sub-Phase 2: The Context Toolkit (`tools/context/`)**

  1.  **Create `tools/context/load_component.sh`:** This script is the mechanism for on-the-fly source code injection.

      - **Function:** It will accept a component name as an argument (e.g., `./tools/context/load_component.sh PersistenceLayer`).
      - **Action:** It reads `docs/components.json`, finds all files associated with that component, purifies their source code using `tools/refine_context.py`, and prints the full, concatenated source code to standard output.
      - **Use Case:** When the AI determines it needs to see the implementation of a "cold" component, it will issue the directive `[DIRECTIVE: LOAD_COMPONENT_SOURCE(component="PersistenceLayer")]`. The human operator will then run this script and paste the output back into the conversation.

  2.  **Update `tools/generate_context.sh`:** The master assembler will be enhanced.
      - **Add a "Toolbox" Preamble:** Before listing the components, the script will now inject a new static section into `CONTEXT_FOR_AI.txt` called "THE TOOLBOX". This section will explicitly list the directives the AI can issue, teaching it how to use its new capabilities.

- **Sub-Phase 3: The Architectural Toolkit (`tools/architecture/`)**

  1.  **Create `tools/architecture/refactor.py`:** This is the heart of our new dynamic system. It will be a robust Python script that safely modifies the `docs/components.json` manifest and its associated abstracts. It will be driven by command-line arguments that mirror the C2I directives.

  2.  **Implement Sub-Commands:**

      - `python3 tools/architecture/refactor.py --migrate-file <path> --from <comp> --to <comp>`: Moves a file's entry in `components.json` from one component to another.
      - `python3 tools/architecture/refactor.py --create-component <name> --description "<desc>"`: Creates a new, empty component entry in the manifest and a corresponding blank abstract file in `docs/component_abstracts/`.
      - `python3 tools/architecture/refactor.py --delete-component <name>`: Removes a component from the manifest and archives its abstract.
      - `python3 tools/architecture/refactor.py --add-to-component <name> --file <path>`: Adds a new file path to an existing component's file list.
      - `python3 tools/architecture/refactor.py --remove-from-component <name> --file <path>`: Removes a file path from a component's file list.

  3.  **Built-in Safeguards:** The script will perform validation before saving changes (e.g., preventing the migration of a file to a non-existent component).

- **Sub-Phase 4: The Governance Protocol (The Workflow)**

  1.  **On-the-Fly Injection:**

      - **AI:** Encounters a problem requiring deeper context. Emits `[DIRECTIVE: LOAD_COMPONENT_SOURCE(component="...")]`.
      - **Human:** Copies the command, runs `./tools/context/load_component.sh ...`, and pastes the full source code output into the next prompt for the AI.

  2.  **Architectural Refactoring:**
      - **AI:** Determines a file is in the wrong component or a new component is needed. Emits `[DIRECTIVE: MIGRATE_FILE(...)]` or `[DIRECTIVE: CREATE_COMPONENT(...)]`.
      - **Human:** Copies the corresponding command, runs `python3 tools/architecture/refactor.py ...`.
      - **Human:** Runs `make test` to verify the change didn't break anything conceptually.
      - **Human:** Commits the modified `docs/components.json` and any new/moved abstracts.
      - **Human:** Regenerates the context for the next turn using the updated architecture.

## IV. THE TOOLBOX (To be added to `CONTEXT_FOR_AI.txt`)

```plaintext
# 🔱 PART 2: THE TOOLBOX (Available C2I Directives)
# You can issue the following directives to request actions from the operator.

---
# Directive: Load Component Source Code
# Usage: When you need to see the full implementation of a "cold" component.
[DIRECTIVE: LOAD_COMPONENT_SOURCE(component="<ComponentName>")]
---
# Directive: Refactor System Architecture
# Usage: When you determine the component architecture itself needs to be modified.
[DIRECTIVE: MIGRATE_FILE(file="<path/to/file.py>", from="<SourceComponent>", to="<TargetComponent>")]
[DIRECTIVE: CREATE_COMPONENT(name="<NewComponentName>", description="<A brief description>")]
[DIRECTIVE: DELETE_COMPONENT(name="<ComponentName>")]
[DIRECTIVE: ADD_TO_COMPONENT(name="<ComponentName>", file="<path/to/file.py>")]
[DIRECTIVE: REMOVE_FROM_COMPONENT(name="<ComponentName>", file="<path/to/file.py>")]
---
```

## V. Acceptance Criteria

- **AC-1:** The C2I `[DIRECTIVE: ...]` protocol is formally defined and documented.
- **AC-2:** The script `tools/context/load_component.sh` exists and correctly prints the full, purified source code of any given component.
- **AC-3:** The script `tools/architecture/refactor.py` exists and correctly implements the `--migrate-file`, `--create-component`, `--delete-component`, `--add-to-component`, and `--remove-from-component` functionalities, safely modifying `docs/components.json`.
- **AC-4:** The main `tools/generate_context.sh` script is updated to include the "THE TOOLBOX" section in its output.
- **AC-5:** The `make test` command completes with 100% success after any refactoring operation.
- **AC-6 (Simulated Refactoring):** A test procedure is successfully executed:
  1.  The AI is prompted to refactor the architecture.
  2.  It issues a `MIGRATE_FILE` directive.
  3.  The human operator runs the corresponding `refactor.py` command.
  4.  The change is observed in `docs/components.json`.
  5.  A new context is generated, reflecting the change.
  6.  `make test` passes.
