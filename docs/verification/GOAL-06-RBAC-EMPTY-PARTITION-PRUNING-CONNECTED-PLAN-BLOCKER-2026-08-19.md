# Goal 6 RBAC empty-partition pruning — connected-plan blocker

Date: `2026-08-19`

Status: **SUPERSEDED BY A VALID RETRY PLAN — ERRORED ARTIFACT REMAINS NOT APPLYABLE**

## Approved scope

The approved checkpoint permitted only:

1. updating ignored development tfvars to the exact pushed verifier digest;
2. offline preflight;
3. AWS identity/Region and existing backend revalidation;
4. one saved connected development plan; and
5. machine-readable review.

It did not permit apply, an ECS task, another ECR push, Doris SQL, Databricks
mutation, destroy, or another infrastructure mutation.

## Input and offline preflight

The ignored input now uses:

```text
736956442295.dkr.ecr.ap-southeast-1.amazonaws.com/ask-david-development/doris-verifier@sha256:a0baa9a180cbe58d6b9cdfb9042ff87b2dec355af45d97a1191890f854b653c9
```

`goal_6_verifier_tasks_enabled` remains `true`.

| Check | Result |
| --- | --- |
| Goal 6 static validator | PASS |
| Goal 5/6 focused regression suite | PASS — 50 tests |
| Terraform recursive format check | PASS |
| Backend-disabled Terraform init | PASS using exact locked providers in an isolated `/tmp` data directory |
| Terraform validate | PASS |
| Development Terraform tests | PASS — 7 passed, 0 failed |
| Diff integrity | PASS |

The default pytest coverage arguments could not load because `pytest-cov` is
not installed; the focused suites used `-o addopts=''`. The two emitted
warnings concern pre-existing `.pytest_cache` write permissions and do not
represent test failures.

## Connected attempt

Read-only identity revalidation returned:

- account `736956442295`;
- Region `ap-southeast-1`; and
- principal `arn:aws:iam::736956442295:user/bach_dev_admin_david`.

The isolated data directory successfully reconfigured against the existing
reviewed S3 backend. Terraform plan used `-lock=false` and refreshed current
AWS and Databricks state, but exited `1` after these Databricks failures:

- current-metastore and workspace entitlement reads returned `unexpected EOF`;
- account OAuth token refresh for profile `ask-david-account` timed out and
  requested a new interactive login.

No retry was performed.

## Rejected artifact

Terraform wrote:

```text
/tmp/goal-06-rbac-empty-partition-pruning-task-definitions-20260819.tfplan
```

| Attribute | Value |
| --- | --- |
| SHA-256 | `209bc05ed666fcc874b37085278fdcf3bc23eff78cc4d5ec07e0171733734a90` |
| Size | `198,100` bytes |
| Terraform / plan format | `1.15.8` / `1.2` |
| `applyable` | `false` |
| `complete` | `false` |
| `errored` | `true` |

This artifact is explicitly **not eligible for apply** and must never be used
as an approval target.

Its incomplete preview contains only:

1. `module.doris_verifier.aws_ecs_task_definition.admin[0]` —
   `delete,create`, replacement path `container_definitions`;
2. `module.doris_verifier.aws_ecs_task_definition.verifier[0]` —
   `delete,create`, replacement path `container_definitions`; and
3. the corresponding two output updates.

Both image changes point from revision-11 digest
`sha256:9401b7bcd881726df2d6bcc7dbe80993a67a9a11b73b21384edba186f2ea061e`
to exact new digest
`sha256:a0baa9a180cbe58d6b9cdfb9042ff87b2dec355af45d97a1191890f854b653c9`.
Although this partial preview matches expected scope, it cannot prove a
complete plan because provider refresh failed.

## Recovery boundary

The user must interactively restore the `ask-david-account` OAuth profile and
verify the `ask-david-development` workspace profile without sharing tokens or
credentials. After that, a new connected saved-plan attempt requires separate
approval. The errored artifact above must not be applied or reused. No apply,
ECS task, Doris SQL, ECR push, Databricks mutation, or other infrastructure
mutation occurred in this checkpoint.

After the user restored both OAuth profiles and separately approved one new
attempt, the retry produced a complete, applyable saved plan at a different
path. The errored artifact documented here was preserved and never reused.
Recovery evidence is
`docs/verification/GOAL-06-RBAC-EMPTY-PARTITION-PRUNING-TASK-DEFINITIONS-CONNECTED-PLAN-2026-08-19.md`.
