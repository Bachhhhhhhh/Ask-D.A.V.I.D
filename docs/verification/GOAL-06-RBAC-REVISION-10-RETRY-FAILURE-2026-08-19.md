# Goal 6 revision-10 RBAC retry — connected failure

Date: 2026-08-19
Status: **PARTIAL — INSERT/UPDATE DENIED; DELETE PROBE BYPASSED AUTH CHECK**

## Approved retry

The approved operation was exactly one private no-retry RBAC task after the
schema-bearing revision-10 admin refresh completed successfully.

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

Pre-run inspection confirmed both Doris hosts running, the exact ACTIVE
revision/image, and no existing RUNNING verifier task.

## Connected result

| Evidence | Result |
| --- | --- |
| ECS task | `03e18f53e9e146c6bba33c5c485de092` |
| Lifecycle | STOPPED / desired STOPPED |
| Container exit | `1` |
| Private network | subnet `subnet-034f5f1c9bca753f1`, IP `10.42.21.151` |
| Ephemeral ENI | `eni-03547c843bb9014a7`, deleted after stop |
| CloudWatch stream | `verifier/doris-verifier/03e18f53e9e146c6bba33c5c485de092` |
| Retry count | `0` |
| RUNNING verifier tasks after inspection | `0` |

Sanitized operation evidence, in execution order:

```json
{"goal":"goal-06","operation":"rbac-verify","status":"denied","statement_class":"insert","denial_evidence":"authorization_text"}
{"goal":"goal-06","operation":"rbac-verify","status":"denied","statement_class":"update","denial_evidence":"authorization_text"}
{"goal":"goal-06","operation":"rbac-verify","status":"unexpected-allow","statement_class":"delete"}
```

This confirms that the schema-ordering correction worked: `INSERT` and
`UPDATE` reached and were rejected by the authorization layer. The task stopped
at `DELETE` and therefore did not execute CREATE, ALTER, DROP, or unauthorized-
database probes.

## Root cause and mutation safety

The current delete statement is:

```sql
DELETE FROM ask_david_serving_development.goal6_authorization_probe WHERE FALSE
```

Apache Doris 4.0.1 deliberately plans this constant-false predicate as a
`PhysicalEmptyRelation`. `DeleteFromCommand` calls
`processEmptyRelation(...)` and returns before its later
`checkTblPriv(..., PrivPredicate.LOAD)` branch. The success therefore means
"empty delete optimized away," not that the query identity possesses DELETE/
LOAD privilege.

The version-bound implementation is
[`DeleteFromCommand.java`](https://github.com/apache/doris/blob/791725594deffd195e7fae19e00e03c3232f105a/fe/fe-core/src/main/java/org/apache/doris/nereids/trees/plans/commands/DeleteFromCommand.java).

No data was deleted: the exact constant-false plan invokes Doris's empty-
relation no-op path. The evidence is still insufficient for Goal 6 because it
does not demonstrate an authorization-layer rejection.

## Next safe correction

The minimal source remediation is delete-probe-specific:

1. first assert through the query-only identity that a reserved key is absent
   from the disposable authorization table;
2. issue DELETE using that non-constant key predicate instead of `WHERE FALSE`;
3. continue accepting only explicit authorization denial; and
4. keep `unexpected-allow` fail-closed even though the absent-key precondition
   guarantees zero affected rows.

This requires offline source/tests/docs validation, a new immutable image,
task-definition revision plan/apply, and one separately approved retry. No
source change, ECR push, Terraform operation, or additional task is authorized
by this report.
