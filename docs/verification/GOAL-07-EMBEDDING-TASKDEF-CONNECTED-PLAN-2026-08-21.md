# Goal 7 embedding-response task-definition connected plan — 2026-08-21

## Approved boundary

This checkpoint was approved to update the ignored development indexer image
digest, run offline preflight, and create/review one saved connected
Terraform plan. No Terraform apply/destroy, ECS task, ECR push, Databricks
operation, bundle operation, or SQL execution was performed.

## Revalidation and inputs

| Check | Result |
| --- | --- |
| AWS account | PASS — `736956442295` |
| AWS region | PASS — `ap-southeast-1` |
| Source aggregate | `03e29f63f11dd8c35cb158076b9db3a026ad548365eff1c646427fd36a73c39f` |
| ECR image digest | `sha256:c48ee41c63f36a6d42b4494ceba363e37754f08da60fb50e0a2e0906facc47b0` |
| Offline infrastructure preflight | PASS — structurally valid state KMS ARN |
| Goal 7 static validator | PASS |
| Focused Goal 7 tests | PASS — 26 passed |
| Python compilation | PASS |
| `git diff --check` | PASS |

The ignored `infrastructure/environments/development/terraform.tfvars` now
references only the promoted indexer digest; all other Goal 7 inputs were
left unchanged.

## Saved plan

| Attribute | Value |
| --- | --- |
| Plan artifact | `/tmp/goal7-indexer-taskdef-20260821.tfplan` |
| Plan SHA-256 | `53b39f6179e7b098acc6081e49c2bb551d7dc9bbc2d5bfac4a841733221310ee` |
| Plan JSON | `/tmp/goal7-indexer-taskdef-20260821.plan.json` |
| Terraform | `1.15.8` |
| `applyable` / `complete` / `errored` | `true` / `true` / `false` |

## Machine-readable action review

| Address | Actions | Scope |
| --- | --- | --- |
| `module.goal7_indexer.aws_ecs_task_definition.this[0]` | `delete,create` | Register the existing Goal 7 indexer family with the corrected image digest |

Action counts are exactly `1 create`, `1 delete`, and `278 no-op` resources;
there are zero unrelated resource updates, replacements, or destroys. The
only changing output is the indexer task-definition ARN. Existing private
subnets, security group, task role, execution role, secret reference, command,
warehouse, AOSS endpoint, and log configuration remain unchanged.

## Current checkpoint

The saved plan is **AWAITING SEPARATE HASH-BOUND APPROVAL TO APPLY**. Goal 7
remains **UNVERIFIED**. No ECS task is authorized by this report.
