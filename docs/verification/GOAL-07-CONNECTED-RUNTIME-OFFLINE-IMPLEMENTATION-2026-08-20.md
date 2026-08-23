# Goal 7 connected runtime boundary — offline implementation — 2026-08-20

## Status

**IMPLEMENTED OFFLINE — CONNECTED DEMO NOT STARTED**

This checkpoint adds the missing deployment boundary for the final integrated
demo. It does not create a Terraform plan, push an image, mutate AWS or
Databricks, run an ECS task, or call Doris/AOSS from the development host.

## Runtime boundary

- `connected.py` supplies three deployment-only adapters: a TLS-only,
  SELECT-only Doris executor; a fixed Databricks analytics query executor; and
  a Databricks-backed canonical embedding provider plus AOSS retrieval adapter.
- `connected_demo.py` builds the existing LangGraph graph and invokes exactly
  the Supervisor plus the three specialized agents for the approved synthetic
  question. It fails closed unless all three agent results succeed.
- `goal7-demo` is a second disabled-by-default Fargate task definition. It uses
  the existing private application network, workload task role, runtime log
  group, workflow OAuth secret, and Goal 6 query secret. It has no direct agent
  infrastructure API or public network path.
- The only new private network rule is workload SG → Doris FE SG TCP/9030. The
  existing indexer rule remains workload SG → AOSS endpoint SG TCP/443.
- `Dockerfile.goal7-runtime` pins LangGraph `1.2.9` and PyMySQL `1.2.0`, runs
  as UID/GID `65532`, and uses the connected demo entry point. The same image
  digest may be used by the gated indexer task with its explicit command
  override.

## Offline validation

| Check | Result |
| --- | --- |
| Goal 7 static validator | PASS — `python3 scripts/validate_goal7.py` |
| Focused tests | PASS — 12 tests via `pytest -o addopts='' -q tests/unit/test_goal7_static.py` |
| Compile check | PASS — `python3 -m compileall -q packages/goal7-runtime/src/ask_david_goal7` |
| Ruff check/format | PASS |
| Terraform format | PASS — root, Goal 7 demo/indexer, IAM, Goal 4 identity, and runtime modules |
| Connected behavior | UNVERIFIED — requires the separately approved digest-pinned image, saved Terraform plan/apply, and one ECS task |
| Local container build | PASS — exact local digest `sha256:c854fe57c92ad16be5cdb9935cfa16736164749a9812c9183157ad9417fae84f`; build and non-root/network-disabled import evidence is recorded in `GOAL-07-RUNTIME-IMAGE-BUILD-2026-08-20.md` |
| Vulnerability scan | UNVERIFIED — no `trivy` or `grype` binary is installed in the current environment |

## Required connected sequence

1. Scan the built runtime image with an approved scanner and push one
   immutable digest to the existing private runtime repository.
2. Enable the ignored development indexer and integrated-demo gates with that
   digest; run offline preflight.
3. Create and inspect one saved connected Terraform plan. Expected actions are
   limited to the Terraform-created workflow service-principal secret, one
   KMS-encrypted Secrets Manager container/version, the exact task-execution
   secret policy, two gated task definitions, and the two private SG rules;
   unexpected replacement/destroy/public/production changes stop the plan.
4. After plan approval and apply, run the indexer once, then run the integrated
   demo once. No implicit retry or ad-hoc mutation is allowed.
