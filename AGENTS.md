# Project Instructions

## Mandatory reading

Before planning or implementing any goal, read:

1. `docs/MASTER_GOAL.md`
2. `docs/ARCHITECTURE.md`
3. `docs/NON_GOALS.md`
4. `docs/ROADMAP.md`
5. All accepted ADRs under `docs/adr/`

These documents define mandatory architecture constraints.

## Fixed architecture constraints

The following decisions must not change without a new approved ADR:

- Unity Catalog is the primary catalog.
- Amazon S3 and Apache Iceberg are the system of record.
- Apache Doris is only a rebuildable low-latency serving layer.
- Amazon OpenSearch Serverless is the vector and document retrieval layer.
- LangGraph is the agent orchestration runtime.
- The MVP contains exactly three specialized sub-agents:
  1. Structured Data Agent
  2. Unstructured Data / RAG Agent
  3. Analytics Agent
- Agents must not directly access data infrastructure.
- All data access must pass through controlled tool services.
- Generated or user-provided code must not execute inside the agent runtime.
- Actual Green SM data is out of scope until synthetic infrastructure validation succeeds.

## Planning requirements

Before implementing a goal:

1. Inspect the repository.
2. Read all mandatory architecture documents.
3. Identify the goal dependencies.
4. Identify files to create or modify.
5. Identify architecture and security risks.
6. List missing environment-specific values.
7. Define validation commands.
8. Define the stopping condition.
9. Do not implement until the plan has been reviewed when planning was explicitly requested.

## Implementation requirements

- Implement only the requested goal.
- Do not expand the scope into future roadmap goals.
- Do not silently change an accepted ADR.
- Do not introduce additional specialized agents.
- Do not add direct infrastructure access to agent code.
- Do not store credentials or secrets in the repository.
- Do not automatically deploy production resources.
- Do not run destructive infrastructure operations without explicit approval.
- Prefer typed interfaces and versioned schemas.
- Add tests for new behavior.
- Update documentation when implementation changes repository behavior.

## Validation requirements

After making changes:

1. Run all relevant formatting checks.
2. Run static analysis.
3. Run type checks.
4. Run unit tests.
5. Run security checks where available.
6. Report commands that could not be run.
7. Report assumptions and manual steps.
8. Compare the result against the current goal acceptance criteria.
9. Do not claim completion when a required criterion is unverified.

## Final report format

Every completed goal must report:

1. Goal summary
2. Files created
3. Files modified
4. Commands executed
5. Tests passed
6. Tests failed
7. Tests not run
8. Architecture decisions affected
9. Security implications
10. Assumptions
11. Manual actions remaining
12. Known limitations
13. Acceptance-criteria result
14. Recommended next roadmap goal

## Git behavior

- Do not delete unrelated files.
- Do not rewrite unrelated history.
- Keep each roadmap goal isolated.
- Do not commit unless explicitly requested.
- Before completion, show the repository status and changed-file summary.
