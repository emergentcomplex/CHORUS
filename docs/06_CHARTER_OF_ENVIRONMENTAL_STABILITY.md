# Filename: docs/06_CHARTER_OF_ENVIRONMENTAL_STABILITY.md

# 🔱 The Charter of Environmental Stability

_Document Version: 1.0_
_Last Updated: 2025-08-08_

---

## Part 1: The Mandate of Resilience

> ✨ A foundation cannot be trusted if it is not stable. An engine cannot be built upon shifting sands. ✨
>
> The CHORUS platform's architecture is the result of a long and arduous process of verification and failure analysis. The stability of our three-environment system (Production, Development, Test) is not an accident; it is an engineered outcome and our most critical asset.
>
> This Charter codifies the inviolable principles that protect this foundation. It is the supreme law governing all interactions with the project's infrastructure. Adherence to this charter is non-negotiable, as it is the source of our trust in the system's resilience and our ability to develop with deliberate velocity.

---

## Part 2: The Axioms of Environmental Architecture

_These Axioms are to be considered an extension of the main CHORUS Constitution._

**77. Axiom of Configuration Precedence:** The configuration defined _inside_ a Docker Compose file (e.g., in an `environment` block) is the absolute, final authority for that service's runtime environment. It MUST take precedence over any and all external sources, including `.env` files and host machine shell variables. Test environments, in particular, MUST be architecturally incapable of being polluted by their host.

**78. Axiom of Explicit Naming:** All resources that could conflict between concurrent environments (containers, networks, volumes) MUST be given a globally unique name. This name MUST be programmatically derived from the environment's unique project name (e.g., `chorus-dev-postgres`). Relying on Docker's default, transient naming for concurrent operations is a proven anti-pattern.

**79. Axiom of Idempotent Orchestration:** All primary `make` targets for starting an environment (e.g., `make run-dev`) MUST be idempotent. They must be architecturally designed to produce the exact same healthy, running state, regardless of the system's state before the command was run. This is achieved by ensuring the first step of any "up" command is a complete and robust "down" command for that specific environment.

**80. Axiom of Headless Verification:** The primary verification environment (`test`) MUST be completely headless. It shall not expose any ports to the host machine. This architecturally guarantees that it can run concurrently with any other environment without any possibility of a network port conflict.

**81. Axiom of Infrastructure Sanctity:** The core infrastructure configuration files (`Makefile`, all `docker-compose.*.yml` files, all `.env.*` files) are now considered a stable, verified baseline. They shall not be modified unless a new mission explicitly and justifiably requires an infrastructure change. Any proposed change to these files must be treated with the highest level of scrutiny and be accompanied by a formal amendment proposal.
