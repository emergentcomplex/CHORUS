# 🔱 Praxis: The Mandate of Signal Purity (Ratified)

## I. Objective

To reduce the input context size for our AI development sessions from ~140K tokens to a target of under 100K tokens. This will be achieved by strategically refining the context generation process to eliminate redundancy, prune non-essential files and data, and programmatically remove low-signal code comments and boilerplate. This mandate will produce a leaner, more potent context file, ensuring faster and more focused development cycles for all future missions.

## II. Guiding Precepts & Inviolable Constraints

**A. The Axiom of Signal Purity:**
The sole purpose of the `CONTEXT_FOR_AI.txt` file is to provide high-signal, mission-critical information. All noise—including verbose data, redundant documentation, secrets, and non-essential code comments—MUST be eliminated.

**B. The Mandate of Verifiability:**
This mission alters the _representation_ of the codebase for the AI, not the codebase itself. The source code on disk must remain untouched by the refinement process. The final state of the repository MUST pass the entire `make test` suite, proving that no functional changes have occurred.

**C. The Principle of Automation:**
The context refinement process MUST be fully automated and integrated into a single, robust `generate_context.sh` script. Manual cleaning or file selection is a forbidden anti-pattern.

## III. The Ground Truth (The Current State)

1.  **Foundationally Stable:** The `make test` command and the CI/CD pipeline are now 100% deterministic and reliable. Our verification harness is sound.
2.  **Context Bloat:** The `CONTEXT_FOR_AI.txt` file is approximately 140K tokens, exceeding efficient processing limits.
3.  **Over-Inclusivity:** The current `generate_context.sh` script includes massive, low-signal directories, most notably `/datalake` and `/models`, which contribute tens of thousands of tokens of non-essential data.
4.  **Redundancy:** The script's logic is flawed, causing it to include documentation in the header and then include it _again_ when scanning the codebase, leading to significant duplication.
5.  **Verbosity:** The codebase includes numerous comments, docstrings, and blank lines that, while useful for human developers, are often low-signal for an AI that can infer logic from the code's structure.

## IV. The Plan

This mission will be executed in three atomic, verifiable sub-phases, culminating in a single, unified, and intelligent script.

- **Sub-Phase 1: The Scribe's Tools (Create the Code Purifier)**

  1.  **Create `tools/refine_context.py`:** This new Python script will be our automated code purifier. It will accept a file path as an argument and print a refined version of the file to standard output. Its functions will be:
      - To programmatically remove all `#`-style comments.
      - To programmatically remove all docstrings (`"""..."""` and `'''...'''`).
      - To remove excessive blank lines, collapsing multiple blank lines into a single one.
      - It MUST use Python's `ast` and `tokenize` libraries for robust parsing, not brittle regular expressions.

- **Sub-Phase 2: The Mandate of Unification (Implement the New Master Script)**

  1.  **Replace `tools/generate_context.sh`:** The existing, flawed script will be completely replaced with the new, state-aware, single-pass version.
  2.  **Implement Single-Pass Logic:** The new script will:
      - Write the Preamble and essential header documents to the context file.
      - As each header file is written, its path will be recorded in a temporary log file (`PROCESSED_FILES_LOG`).
      - Define an expanded `EXCLUDE_PATTERNS` array to prune low-signal directories like `/datalake`, `/models`, `/logs`, and the obsolete `/documentation` file.
      - Perform a single, comprehensive `find` command to gather all remaining files.
      - Pipe the results of `find` through a `grep` filter that removes any file already listed in the `PROCESSED_FILES_LOG`, thus guaranteeing no duplication.
      - Append the content of the remaining, valid files, using the `refine_context.py` purifier for all Python source code.
  3.  **Delete `tools/generate_verified_context.sh`:** This script is now obsolete and MUST be deleted to prevent future confusion.

- **Sub-Phase 3: The Final, Verifiable Signal (Verification & Comparative Analysis)**
  1.  **Establish Baseline:** Execute the _original_ `generate_context.sh` script (before its replacement) and save its output as `CONTEXT_BASELINE.txt`.
  2.  **Implement Refinements:** Execute the changes from Sub-Phases 1 and 2.
  3.  **Generate New Context:** Execute the _new_ `generate_context.sh` with the "Mandate of the Oracle" mission file (`docs/missions/00_mandate_of_the_oracle.md`) as the argument, creating the final `CONTEXT_FOR_AI.txt`.
  4.  **Quantitative Verification:** Compare the token counts (approximated by word count) of `CONTEXT_BASELINE.txt` and `CONTEXT_FOR_AI.txt`, asserting a reduction of at least 30%.
  5.  **Qualitative Verification:** Perform a `diff` on the lists of included filenames between the baseline and the new context to prove that the correct files were excluded and no essential source code was lost.
  6.  **Final Integrity Check:** Execute `make test` to provide absolute certainty that the underlying codebase remains valid and fully functional.

## V. Acceptance Criteria

- **AC-1:** The new script `tools/refine_context.py` exists and successfully removes comments, docstrings, and excess blank lines from Python files.
- **AC-2:** The obsolete script `tools/generate_verified_context.sh` is **deleted** from the repository.
- **AC-3:** The new `tools/generate_context.sh` script is in place and correctly implements the single-pass, state-aware, duplication-proof logic.
- **AC-4:** The final `CONTEXT_FOR_AI.txt` generated by the new process is verifiably under 100,000 tokens.
- **AC-5:** The `make test` command completes with 100% success, proving the codebase's integrity is unharmed.
- **AC-6 (Comparative Analysis):** A verifiable, automated comparison between the baseline and the new context file proves:
  - A token count reduction of at least 30%.
  - The successful exclusion of the `/datalake`, `/models`, and secret files.
  - The preservation of all essential `chorus_engine` source files.
