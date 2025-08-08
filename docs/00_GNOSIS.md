# Filename: docs/00_GNOSIS.md

# 🔱 The Gnosis (The Distilled Wisdom)

_This document contains key excerpts from our foundational texts. These principles are the distilled wisdom that informs our Constitution and our architecture._

---

#### From 'Clean Architecture' by Robert C. Martin:

> **On the Goal of Architecture:** 'The goal of software architecture is to minimize the human resources required to build and maintain the required system.'
> **On the Dependency Rule:** 'Source code dependencies must point only inward, toward higher-level policies. Nothing in an inner circle can know anything at all about something in an outer circle.'
> **On Irrelevant Details:** 'The GUI is a detail... The database is a detail... Frameworks are not architectures. Keep it at arm’s length. Treat the framework as a detail.'

---

#### From 'Designing Data-Intensive Applications' by Martin Kleppmann:

> **On Reliability, Scalability, and Maintainability (Ch 1):** These are the three primary concerns. Reliability means tolerating faults to prevent failures. Scalability means having strategies to cope with load. Maintainability means designing for operability, simplicity, and evolvability.
> **On the Unbundled Database (Ch 12):** Dataflow systems can be seen as an unbundling of database components. Event logs (like Kafka) act as the commit log. Stream processors act as the trigger/stored procedure/index-maintenance engine. This allows composing specialized tools in a loosely coupled way.
> **On Integrity vs. Timeliness (Ch 12):** 'I am going to assert that in most applications, integrity is much more important than timeliness.'

---

#### From 'Unit Testing: Principles, Patterns, and Practices' by Vladimir Khorikov:

> **On the Goal of Unit Testing:** 'The goal of unit testing is to enable sustainable growth of a software project.'
> **On What to Test (Observable Behavior):** 'You should test only the observable behavior of the SUT (System Under Test)... An observable behavior is a behavior that can be perceived by the SUT’s clients.'
> **On Mocks vs. Stubs:** 'Remember this simple rule: stubs can’t fail tests; mocks can... Use mocks to verify interactions between the SUT and its collaborators. Use stubs to feed the SUT with data.'
> **On the Four Pillars of a Good Unit Test:** 'A good unit test has four attributes: 1. It provides protection against regressions. 2. It is resistant to refactoring. 3. It provides fast feedback. 4. It is maintainable.'
