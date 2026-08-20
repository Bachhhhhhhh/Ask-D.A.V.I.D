# Goal 6 RBAC DELETE-probe remediation — task-definition connected plan

Date: `2026-08-19`

Status: **PLAN REVIEWED AND SUBSEQUENTLY APPLIED — NO TASK EXECUTED**

## Approved scope

The approved checkpoint changed only the ignored development verifier image
input to the exact scanned ECR digest, retained
`goal_6_verifier_tasks_enabled = true`, ran offline preflight, reverified the
development AWS identity, and created one saved connected plan. It did not
authorize or perform apply, ECS task execution, ECR push, Doris SQL, Databricks
mutation, destroy, or any other infrastructure mutation.

## Bound environment and artifact

| Attribute | Value |
| --- | --- |
| AWS account / Region | `736956442295` / `ap-southeast-1` |
| New image digest | `sha256:9401b7bcd881726df2d6bcc7dbe80993a67a9a11b73b21384edba186f2ea061e` |
| Saved plan | `/tmp/goal-06-rbac-delete-probe-task-definitions-20260819.tfplan` |
| Saved-plan SHA-256 | `decb5329e0c7b7d811525da23d1a607ee8527c4b1a197e6adcea9cfdc88a4dcf` |
| Artifact size | `209,405` bytes |
| Terraform version / plan format | `1.15.8` / `1.2` |

The plan used the existing S3 backend with `-lock=false`, so remote state was
read without creating an external lock object; only the local saved-plan
artifact was created.

## Offline preflight

| Check | Result |
| --- | --- |
| Goal 6 static validator | PASS |
| Goal 5/6 focused Python regression suite | PASS — 50 tests |
| Terraform recursive format check | PASS |
| Terraform validate | PASS |
| Development Terraform tests | PASS — 7 passed, 0 failed |
| Diff integrity | PASS |

The repository `.terraform` cache was writable only by `nobody`, so the first
validation attempt reported missing newly added local modules. No backend or
state operation occurred in that failed attempt. Rather than changing shared
cache ownership, an isolated `TF_DATA_DIR` under `/tmp` was initialized first
with backend disabled and lockfile readonly. Validation/tests then passed. The
same isolated directory was reconfigured against the existing reviewed S3
backend only for the connected plan.

The two pytest warnings concern inability to update `.pytest_cache`; all tests
passed and no acceptance result depends on that cache.

## Machine-readable plan review

Action inventory:

| Actions | Count |
| --- | ---: |
| `delete,create` replacement | 2 |
| `no-op` | 257 |
| In-place update | 0 |
| Create-only | 0 |
| Destroy-only | 0 |

The only managed changes are:

1. `module.doris_verifier.aws_ecs_task_definition.admin[0]`;
2. `module.doris_verifier.aws_ecs_task_definition.verifier[0]`.

For both resources:

- resource type is `aws_ecs_task_definition`;
- replacement path is only `container_definitions`;
- the prior image is the deployed revision-10 digest
  `sha256:c7e9cbc1e0a330fe17397d5509f0ec4618a450b489b342128ef20c59040834c6`;
- the new image is the exact scanned/pushed digest
  `sha256:9401b7bcd881726df2d6bcc7dbe80993a67a9a11b73b21384edba186f2ea061e`.

Only the corresponding two task-definition ARN outputs become unknown until
apply. There is no IAM, KMS, network/security-group, ECR, EC2/EBS, S3,
Databricks, metastore, warehouse, public-exposure, production, or Goal 7+
managed-resource action.

Terraform represents registering a new task-definition revision and removing
the prior revision from state as `delete,create`; it does not delete an ECS
service, running task, host, volume, or data resource. No task is run by apply.

## Apply boundary

Only the exact saved artifact and SHA-256 above are eligible for apply. Before
apply, identity/account/Region and the artifact hash must be reverified. Apply
must stop on hash mismatch and may not generate an implicit replacement plan.
Immediate post-apply inspection may verify the two new ACTIVE revisions,
digest, Fargate/`awsvpc` shape, and no RUNNING task. A one-shot RBAC verifier
retry requires a later independent approval.

The exact hash-bound plan was subsequently applied under separate approval.
Evidence is recorded in
`docs/verification/GOAL-06-RBAC-DELETE-PROBE-TASK-DEFINITIONS-APPLY-2026-08-19.md`.
