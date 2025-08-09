# Filename: docs/05_FAILED_HYPOTHESES.md

# 🔱 The CHORUS Graveyard of Failed Hypotheses

_This document is a core part of our systemic learning process, fulfilling **Axiom 35**. It codifies the flawed assumptions and failed architectural patterns that have been tested and proven incorrect during development. All core developers MUST internalize these lessons to prevent repeating past failures._

---

### **Part 1: Flawed Technical Hypotheses**

**Hypothesis #1: The Host is a Valid Executor**

- **The Flawed Belief:** A `make` target is a simple shortcut, and it is acceptable for it to execute a Python script directly on the host machine for convenience.
- **The Manifestation (The Error):** `failed to remove file ... .venv/.lock: Permission denied`. An unpredictable, environment-specific file permission error.
- **The Ground Truth (The Reason for Failure):** This directly violated **Axiom 69 (The Unified Environment)**. The host machine is an orchestrator, not an executor. Its environment is inconsistent and cannot be trusted. The canonical environment exists _only_ inside the container.
- **The Lesson:** All CHORUS processes—without exception—run inside a container. The `Makefile`'s role is to tell Docker _what_ to run, not to run it itself.

**Hypothesis #2: The Environment is Implicit**

- **The Flawed Belief:** A script's dependencies (like the `git`, `psql`, or `curl` clients) will implicitly be available in the container environment where it runs.
- **The Manifestation (The Error):** `psql: not found` or `git: command not found`.
- **The Ground Truth (The Reason for Failure):** A container's environment is brutally explicit. It contains _only_ what its `Dockerfile` installs. Our `setup-connector.sh` script depended on `psql` and `curl`, but the minimal base image we chose for that service did not provide them.
- **The Lesson:** The `Dockerfile` is the single, absolute source of truth for the capabilities of a runtime environment. Every dependency a script has must be explicitly declared and installed in the `Dockerfile` for the image that script will run in.

**Hypothesis #3: The "Lean Artifact" is Just About File Copying**

- **The Flawed Belief:** Creating a lean production image simply means copying the `chorus_engine` source folder into a slim container alongside the installed libraries.
- **The Manifestation (The Error):** A total system collapse. `uv: command not found`, `python: can't find '__main__' module`, `pytest: No such file or directory`.
- **The Ground Truth (The Reason for Failure):** A Python application is not just a folder of files. It must be formally **installed** into the environment (e.g., via `pip install .`) for the interpreter to recognize it as a package and for its entry points to be placed on the `PATH`. Our "lean" image was a hollow shell that contained files but no actual, working application.
- **The Lesson:** A lean artifact must first be a **correct and functional** artifact. We must follow standard, canonical Python packaging practices (`pip wheel` or `pip install`) to build our images.

**Hypothesis #4: The "Two Worlds" Can Be Reconciled with Patches**

- **The Flawed Belief:** The fundamental incompatibility between a broken `production` image and a working `development` image could be fixed by patching symptoms (e.g., adding `uv` to the production image, setting `PYTHONPATH`).
- **The Manifestation (The Error):** A long, frustrating loop of different but related failures. Each patch simply revealed a deeper layer of the same fundamental problem.
- **The Ground Truth (The Reason for Failure):** The "Two Worlds" anti-pattern cannot be reconciled; it must be eliminated. The root cause was a broken `Dockerfile` that created two different, incompatible environments. No amount of patching could fix a broken build artifact.
- **The Lesson:** When development and testing/production environments diverge and produce different results, the problem is almost always a flaw in the build process itself. Suspect the `Dockerfile` first.

**Hypothesis #5: The Docker Cache is Always Your Friend**

- **The Flawed Belief:** Running `make build` is sufficient to apply changes made to a `Dockerfile`.
- **The Manifestation (The Error):** The exact same error (`psql: not found`) repeated even after the `Dockerfile` for the setup utility was corrected.
- **The Ground Truth (The Reason for Failure):** Docker's layer cache is extremely aggressive. It saw that the initial lines of the `Dockerfile` hadn't changed and decided to use the old, cached layers, completely ignoring the corrective commands. This can also manifest as a `run` command executing a container based on an old, stale image tag.
- **The Lesson:** When making foundational changes to a `Dockerfile` (installing new tools, changing base images, altering fundamental build steps), the cache must be explicitly invalidated with `docker compose build --no-cache` or by ensuring images are tagged with unique names.

**Hypothesis #6: A Tool's Capabilities Can Be Assumed**

- **The Flawed Belief:** I can assume how a complex, third-party tool (like the official PostgreSQL Docker image) works based on convention, without consulting its documentation.
- **The Manifestation (The Error):** The `wal_level >= logical` error, which proved our custom `postgresql.conf` was not being loaded.
- **The Ground Truth (The Reason for Failure):** I hallucinated a configuration method that does not exist. I repeatedly failed to ground my implementation in authoritative, external documentation. The official documentation clearly states that custom server arguments should be passed via the `command` directive.
- **The Lesson:** Trust, but verify. Never assume a tool's functionality. Always consult the official documentation for the exact, canonical method of configuration and operation.

**Hypothesis #7: A Shared Default Volume is Safe.**

- **The Flawed Belief:** Docker Compose will correctly manage data for different environments using its default, unnamed volumes.
- **The Manifestation (The Error):** `psycopg2.OperationalError: FATAL: database "trident_analysis" does not exist` in the development environment after running the test suite, despite the test suite passing.
- **The Ground Truth (The Reason for Failure):** Unnamed, default volumes are shared across all compose files for a single project. The `make test` command created a volume containing only the test database. A subsequent `make run` attached this same volume, saw it was not empty, and skipped its own initialization script, meaning the development database was never created.
- **The Lesson:** Environments MUST have explicitly named, isolated resources (especially volumes) to prevent state pollution and ensure true environmental independence.

**Hypothesis #8: Verifying a Side Effect is the Same as Verifying the User Journey.**

- **The Flawed Belief:** If the database shows a task's status is `COMPLETED`, the end-to-end user journey must be working.
- **The Manifestation (The Error):** The E2E test suite passed consistently, yet the UI was completely non-functional, showing a "Not Found" error for all queries.
- **The Ground Truth (The Reason for Failure):** The E2E test was not simulating a true user. The user's view is derived from Redis, which is populated by the CDC pipeline. By polling the database directly, the test completely missed the broken CDC link that was preventing Redis from ever being updated.
- **The Lesson:** E2E tests MUST validate the system from the user's perspective. This means interacting with and verifying the state of the same components the user's browser does (the UI's API and its true underlying data source, in this case, Redis), in strict adherence to **Axiom 72 (True User Simulation)**.

**Hypothesis #9: The Override Model is a Viable Pattern for Distinct Environments.**

- **The Flawed Belief:** A single base `docker-compose.yml` file can be effectively "overridden" with other Compose files (`-f file1.yml -f file2.yml`) to manage three fundamentally different environments (persistent-prod, mutable-dev, ephemeral-test).
- **The Manifestation (The Error):** A persistent, chaotic spiral of failures. `port is already allocated` errors because test-environment overrides failed to remove port mappings. `psql: not found` errors because a dev-environment override took precedence over a base-environment build definition. The system's state was unpredictable and impossible to debug.
- **The Ground Truth (The Reason for Failure):** Docker Compose's file merging logic is designed for minor tweaks, not for defining fundamentally distinct architectures. It creates a complex, implicit dependency graph where the final configuration is non-obvious and prone to subtle, cascading failures. This directly violates the **Axiom of Canonical Simplicity (Axiom 53)**.
- **The Lesson:** Truly distinct environments require truly distinct, self-contained, and explicit configuration files. The orchestrator (the `Makefile`) should be responsible for choosing which single, complete configuration to execute, eliminating all ambiguity and implicit dependencies.

**Hypothesis #10: The Static `container_name` Directive is a Panacea.**

- **The Flawed Belief:** Manually setting `container_name` in the Compose files would solve all concurrency issues.
- **The Manifestation (The Error):** `Conflict. The container name ... is already in use`.
- **The Ground Truth (The Reason for Failure):** While `container_name` provides uniqueness, it creates static, inflexible names. The true root cause was a race condition in the `Makefile`'s orchestration, where the `down` command for one environment had not fully released its resources before the `up` command for another began. The static names made this race condition _more_ likely to cause a hard conflict.
- **The Lesson:** The orchestration layer (`Makefile`) must be robust first. It must guarantee a clean slate before starting any environment. The solution was not static names, but idempotent `run` commands.

**Hypothesis #11: The Host Environment is Benign.**

- **The Flawed Belief:** The test environment, when run inside a container, would be naturally isolated from the host machine's shell environment.
- **The Manifestation (The Error):** `connection to server at "postgres", port 5434 failed`. The test suite was trying to connect to the `dev` database port, not the `test` database port.
- **The Ground Truth (The Reason for Failure):** Docker Compose's `env_file` directive has a lower precedence than variables already present in the shell environment where the `docker compose` command is run. A `DB_PORT=5434` variable on the host machine "leaked" into the test container, overriding the correct settings from `.env.test`.
- **The Lesson:** A test environment is not hermetic unless it is _architecturally incapable_ of being polluted. The definitive solution is to set critical variables directly in the `docker-compose.test.yml` file's `environment` block, as this has the highest precedence and guarantees true isolation.

**Hypothesis #12: A Simple Typo is Not a Systemic Failure.**

- **The Flawed Belief:** A simple typo, like a mismatched `.env` file project name or a YAML syntax error, is a minor issue.
- **The Manifestation (The Error):** The entire "Great Spiral of Failure."
- **The Ground Truth (The Reason for Failure):** In a complex, multi-environment system, a single configuration error can create cascading failures that present as deep, complex architectural problems. The `COMPOSE_PROJECT_NAME` mismatch in `.env.prod` was the true root cause of many of the container name conflicts.
- **The Lesson:** All configuration is code. It must be treated with the same rigor, scrutiny, and verification as application code. Suspect the simplest possible error first.



**Hypothesis #14: The `.gitignore` is an Infallible Guardian**

-   **The Flawed Belief:** Adding a file path to `.gitignore` is a sufficient and complete security measure to prevent that file from ever being committed to the repository.
-   **The Manifestation (The Error):** The `.secrets` file, containing sensitive API keys, was accidentally staged and committed to the repository, requiring a historical rewrite and a security protocol update.
-   **The Ground Truth (The Reason for Failure):** The `.gitignore` file only prevents *untracked* files from being accidentally added. It does nothing to prevent a file that has been explicitly staged (e.g., via `git add .` or `git add -f`) from being committed. It is a powerful convention, but it is not an enforced security boundary. Human error can and will bypass it.
-   **The Lesson:** Security requires defense-in-depth. The `.gitignore` file is the necessary first layer of defense, but it is insufficient on its own. A second, automated layer, such as a pre-commit hook that explicitly blocks the staging of sensitive files, is required to create a truly resilient and error-proof system. We must automate our security protocols to protect against our own fallibility.

---

### **Part 2: Anti-Patterns of Praxis (Flawed Methodologies)**

**Anti-Pattern #1: The Anti-Pattern of Incrementalism.**

- **Description:** Attempting to fix a systemic, architectural failure with a series of small, tactical, and isolated patches.
- **Manifestation:** The "Great Spiral of Failure," where each "fix" for one environment created a new, unforeseen failure in another.
- **The Lesson:** When a system exhibits complex, cascading failures across multiple environments, the correct response is not to patch the immediate symptom. The correct response is to **halt, perform a holistic analysis, and address the root architectural flaw.** A series of small fixes is often more costly than a single, well-planned architectural correction.

**Anti-Pattern #2: The Anti-Pattern of Unverifiable Assumptions.**

- **Description:** Proposing a solution without first gathering the necessary diagnostic data (e.g., logs, configuration dumps) to prove the root cause of the failure.
- **Manifestation:** Repeatedly proposing solutions that failed because they were based on an incorrect assumption about the system's runtime state (e.g., assuming a tool was installed, assuming a configuration was loaded).
- **The Lesson:** All remediation must begin with verification. Before a solution is proposed, a diagnostic protocol must be executed to capture the ground truth of the failure. The **Verifiable Failure Report** is the formal artifact of this process.
