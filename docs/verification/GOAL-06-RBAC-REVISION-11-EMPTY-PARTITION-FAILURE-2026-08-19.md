# Goal 6 revision-11 RBAC verifier — empty-partition failure

Date: `2026-08-19`

Status: **PARTIAL — INSERT/UPDATE DENIED; DELETE PRUNED BEFORE AUTHORIZATION**

## Approved execution

The operation was exactly one private, no-retry RBAC task from
`ask-david-development-doris-verifier:11`, using immutable image digest
`sha256:9401b7bcd881726df2d6bcc7dbe80993a67a9a11b73b21384edba186f2ea061e`.
It ran on `ask-david-development-cluster` in the approved private application
subnets with verifier security group `sg-04eb1ebf613ceeadc`, public IP disabled,
and FE endpoint `10.42.64.238:9030`.

Pre-run inspection confirmed AWS account `736956442295`, Region
`ap-southeast-1`, both Doris hosts RUNNING, the exact ACTIVE task definition
and image, and no existing RUNNING verifier task.

## Connected result

| Evidence | Result |
| --- | --- |
| ECS task | `8a24b56cb8604292ad77c4e260add739` |
| Lifecycle | STOPPED / `EssentialContainerExited` |
| Container exit | `1` |
| Private placement | subnet `subnet-0a1aad220d82ef879`, IP `10.42.44.227` |
| Ephemeral ENI | `eni-07c19316b000ed9ba`, deleted after stop |
| CloudWatch stream | `verifier/doris-verifier/8a24b56cb8604292ad77c4e260add739` |
| Retry count | `0` |
| RUNNING verifier tasks after inspection | `0` |

Sanitized markers, in execution order:

```json
{"goal":"goal-06","operation":"rbac-verify","status":"denied","statement_class":"insert","denial_evidence":"authorization_text"}
{"goal":"goal-06","operation":"rbac-verify","status":"denied","statement_class":"update","denial_evidence":"authorization_text"}
{"goal":"goal-06","operation":"rbac-verify","status":"unexpected-allow","statement_class":"delete"}
```

There was no completion marker. CREATE, ALTER, DROP, and unauthorized-database
probes did not run. The approved stop condition was honored and no retry ran.

## Root cause and mutation safety

The revision-11 runner first proved reserved `TINYINT` key `127` absent, then
attempted DELETE with `WHERE probe_id = 127`. The disposable authorization
table itself was entirely empty. In the pinned Apache Doris 4.0.1 source,
`PruneEmptyPartition` can convert that scan to an empty relation, and
`DeleteFromCommand` returns for a physical empty relation before its later
`LOAD_PRIV` authorization check. This explains why changing from constant
`FALSE` to a non-constant absent-key predicate alone did not reach RBAC.

The successful precondition proves the attempted DELETE had no matching row;
therefore no data was changed. Its success is still insufficient as
principal-specific DELETE denial evidence, so Phase 6-11 remains partial.

Version-bound primary-source references:

- [`DeleteFromCommand.java`](https://github.com/apache/doris/blob/791725594deffd195e7fae19e00e03c3232f105a/fe/fe-core/src/main/java/org/apache/doris/nereids/trees/plans/commands/DeleteFromCommand.java)
- [`PruneEmptyPartition.java`](https://github.com/apache/doris/blob/791725594deffd195e7fae19e00e03c3232f105a/fe/fe-core/src/main/java/org/apache/doris/nereids/rules/rewrite/PruneEmptyPartition.java)
- [`SessionVariable.java`](https://github.com/apache/doris/blob/791725594deffd195e7fae19e00e03c3232f105a/fe/fe-core/src/main/java/org/apache/doris/qe/SessionVariable.java)

## Required correction boundary

The minimal correction is to retain the fail-closed reserved-key absence
precondition, then run `SET disable_empty_partition_prune = true` and the
reserved-key DELETE in the same MariaDB session. Separating the SET into a
different client invocation would not affect the DELETE session.

This report does not authorize or perform an image build/push, Terraform
plan/apply/destroy, ECS task, Doris connected SQL, AWS mutation, or Databricks
operation.
