# Goal 6 revision-10 RBAC verifier — connected failure

Date: 2026-08-19
Status: **FAIL — WRONG REJECTION LAYER; NO RETRY**

## Approved execution

The approved operation was exactly one private no-retry RBAC verifier task
using the Terraform-created revision-10 task definition and immutable
remediation image.

| Bound input | Value |
| --- | --- |
| AWS account / region | `736956442295` / `ap-southeast-1` |
| ECS cluster | `ask-david-development-cluster` |
| Task definition | `ask-david-development-doris-verifier:10` |
| Image digest | `sha256:c7e9cbc1e0a330fe17397d5509f0ec4618a450b489b342128ef20c59040834c6` |
| Private subnets | `subnet-034f5f1c9bca753f1`, `subnet-0a1aad220d82ef879` |
| Verifier security group | `sg-04eb1ebf613ceeadc` |
| Public IP | `DISABLED` |
| FE endpoint | `10.42.64.238:9030` |

Pre-run inspection confirmed both FE `10.42.64.238` and BE `10.42.71.97`
EC2 instances were running, revision `10` was ACTIVE on the exact digest, and
no verifier task was already running.

## Observed result

| Evidence | Result |
| --- | --- |
| ECS task | `c91db7d52e2148c68d38b3d3cd7e07ce` |
| Lifecycle | STOPPED / desired STOPPED |
| Container exit | `1` |
| Task definition | revision `10` |
| Launch type / platform | Fargate / `1.4.0` |
| Private network | subnet `subnet-0a1aad220d82ef879`, IP `10.42.32.153`, ENI deleted after stop |
| CloudWatch stream | `verifier/doris-verifier/c91db7d52e2148c68d38b3d3cd7e07ce` |
| Retry count | `0` |
| Running verifier tasks after inspection | `0` |

The only Goal 6 operation marker was:

```json
{"goal":"goal-06","operation":"rbac-verify","status":"wrong-rejection-layer","statement_class":"insert"}
```

The positive serving-table `SELECT` and the grant inspection occur before the
first negative probe. Reaching this marker therefore shows that those earlier
steps completed, but the failed `INSERT` was not classified as an explicit
authorization denial by the reviewed runner. It does **not** prove that the
`INSERT` was permitted: an allowed statement would emit `unexpected-allow`.

## Root cause

This is a schema-application ordering failure, not a classifier-wording
failure:

1. `goal6_authorization_probe` was introduced in the later verifier source set
   under `doris/schemas/01_serving_database.sql`.
2. The last successful admin refresh used revision `8` and image digest
   `sha256:15442d9d94f001f1e5915013009af50a78bf6ad8112ec34ddc044d6bbd02faad`,
   before that later schema-bearing image was deployed.
3. Revisions `9` and `10` were registered, but no admin-refresh execution using
   either revision occurred before this RBAC task. Registering a task
   definition does not execute the schema migration.
4. The RBAC runner's first negative probe resolves
   `ask_david_serving_development.goal6_authorization_probe`. Apache Doris
   4.0.1 resolves the target table before calling the `LOAD` privilege check.
   A missing target therefore fails outside the authorization layer and is
   correctly classified as `wrong-rejection-layer`.

The version-bound Doris implementation is
[`InsertIntoTableCommand.java`](https://github.com/apache/doris/blob/791725594deffd195e7fae19e00e03c3232f105a/fe/fe-core/src/main/java/org/apache/doris/nereids/trees/plans/commands/insert/InsertIntoTableCommand.java):
`getTargetTableIf(...)` precedes `checkTblPriv(..., PrivPredicate.LOAD)`.
Official 4.0.1 error definitions use `Access denied` for an actual privilege
failure, which the current classifier already recognizes. The classifier must
therefore remain fail-closed rather than accepting the observed non-auth error.

Raw database stderr remains deliberately suppressed, so the exact missing-
object wording is not persisted. The repository migration history, last
successful schema runner revision, and Doris execution order together identify
the omitted schema-application checkpoint.

## Boundary and next action

No retry, second task, SQL mutation, Terraform operation, ECR push,
Databricks operation, public-network change, or production operation occurred.
Phase 6-11 and final acceptance items 34–35 remain unverified. No source,
image, Terraform, or privilege broadening is required. The smallest correction
is one separately approved revision-10 admin-refresh execution. Its
version-controlled `CREATE TABLE IF NOT EXISTS` schema step creates the
disposable authorization target before performing the existing governed full
refresh. Only after that task exits zero may one separately approved RBAC
revision-10 retry run.

## Corrective execution

The separately approved schema-bearing admin refresh subsequently ran exactly
once as task `c08352df6d7846128c7852e3d130b700` and exited `0`. Its CloudWatch
stream contains the terminal `admin-refresh` `completed` marker, its ephemeral
private ENI was deleted after stop, and no admin task remains RUNNING. This
closes the schema-ordering defect without a classifier, image, Terraform, or
privilege change. See
`GOAL-06-RBAC-SCHEMA-ORDERING-ADMIN-REFRESH-CONNECTED-2026-08-19.md`.

The RBAC acceptance result itself remains unverified because no retry was
included in that approval.
