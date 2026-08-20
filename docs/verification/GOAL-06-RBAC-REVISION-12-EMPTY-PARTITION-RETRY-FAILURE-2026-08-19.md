# Goal 6 revision-12 RBAC verifier — empty-partition retry failure

Date: `2026-08-19`

Status: **PARTIAL — INSERT/UPDATE DENIED; DELETE STILL UNEXPECTEDLY ALLOWED**

## Approved execution

The operation was exactly one private, no-retry RBAC task from
`ask-david-development-doris-verifier:12`, using immutable image digest
`sha256:a0baa9a180cbe58d6b9cdfb9042ff87b2dec355af45d97a1191890f854b653c9`.
It ran on `ask-david-development-cluster` using one of the approved private
application subnets, verifier security group `sg-04eb1ebf613ceeadc`, public
IP disabled, and FE endpoint `10.42.64.238:9030`.

Pre-run inspection confirmed AWS account `736956442295`, Region
`ap-southeast-1`, FE `10.42.64.238` and BE `10.42.71.97` both `running`, the
exact ACTIVE revision-12 Fargate/`awsvpc` task definition and image, and zero
existing RUNNING verifier tasks.

## Connected result

| Evidence | Result |
| --- | --- |
| ECS task | `d5dfb96b0dbb46da8c912911baa51889` |
| Task definition | `ask-david-development-doris-verifier:12` |
| Lifecycle | `STOPPED` / `Essential container in task exited` |
| Container exit | `1` |
| Private placement | subnet `subnet-0a1aad220d82ef879`, IP `10.42.35.62` |
| Ephemeral ENI | `eni-00a4162e222f0603e`, deleted after stop |
| CloudWatch stream | `verifier/doris-verifier/d5dfb96b0dbb46da8c912911baa51889` |
| Retry count | `0` |
| RUNNING verifier tasks after inspection | `0` |

Sanitized CloudWatch markers, in execution order:

```json
{"goal":"goal-06","operation":"rbac-verify","status":"denied","statement_class":"insert","denial_evidence":"authorization_text"}
{"goal":"goal-06","operation":"rbac-verify","status":"denied","statement_class":"update","denial_evidence":"authorization_text"}
{"goal":"goal-06","operation":"rbac-verify","status":"unexpected-allow","statement_class":"delete"}
```

The runner stopped at DELETE, so CREATE, ALTER, DROP, and unauthorized-database
probes did not run. The approved no-retry stop condition was honored.

## What this proves and does not prove

Revision 12 contains the reviewed source contract that first checks the
reserved key `127` is absent, then sends `SET disable_empty_partition_prune =
true; DELETE ... WHERE probe_id = 127` in the same MariaDB client invocation.
Nevertheless, the connected result still reports `unexpected-allow` for
DELETE. The available evidence does not establish whether Doris accepted the
setting, still optimized the no-match delete along another path, or evaluated
authorization differently for that statement. It therefore does **not** prove
principal-specific DELETE rejection and does not close the Phase 6-11 RBAC
acceptance criterion.

The absence precondition in the reviewed runner means the attempted DELETE
targeted no matching reserved key. This report records no successful DDL/DML
data mutation; it does not substitute that safety property for required RBAC
denial evidence.

## Required next boundary

No retry, Terraform, ECR, Databricks, AWS mutation, or ad-hoc SQL correction
occurred after the failure. A separate offline root-cause analysis and minimal
remediation proposal is required before any new image build, deployment plan,
or task execution can be considered.
