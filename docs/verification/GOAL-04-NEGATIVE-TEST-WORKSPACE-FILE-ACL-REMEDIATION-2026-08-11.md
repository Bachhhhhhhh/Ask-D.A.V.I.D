# Goal 4 negative-test workspace-file ACL remediation

## Scope and boundary

This report records the failed protected-table negative run and its approved
offline-only bundle ACL remediation. It does not authorize connected bundle
validation/deployment, another job/SQL run, table/data mutation, Terraform, or
AWS operation.

## Failed-run evidence

- Job ID: `187789722076444`.
- Run ID: `401673129115320`.
- Task run ID: `683957801326880`.
- Task: `denied_table_query_must_fail`.
- Attempt: `0`.
- Run/task state: `INTERNAL_ERROR / FAILED`.
- Active runs after completion: `0`.

The task failed before SQL execution:

```text
Failed to fetch object from the remote repository: File
/Workspace/Users/bachvxuan@gmail.com/.bundle/
ask-david-goal-04-lakehouse/development/files/sql/goal_04/
11_denied_table_access.sql not found
```

This is not `PERMISSION_DENIED` from Unity Catalog. It proves neither protected
table rejection nor unintended access, so acceptance criterion 27 remains
UNVERIFIED. No retry or direct-path negative job ran. The existing Small
Serverless SQL warehouse remained inside its 10-minute auto-stop window.

## Root cause

The bundle deploys synchronized SQL under a governance-administrator user
root. The denied service principal has workspace/SQL entitlement and warehouse
access but intentionally has no data grants. It did not have a bundle file ACL,
so the task could not load the neutral SQL that should exercise Unity Catalog.

Databricks documents that top-level bundle permissions apply to resources,
workspace directories, and files. Workspace file `CAN_VIEW` permits reading a
file but not running, editing, or managing it.

## Minimal declarative remediation

The bundle grants the denied service principal exactly one top-level permission:

```yaml
- service_principal_name: ${var.denied_service_principal_application_id}
  level: CAN_VIEW
```

This permission is only the workspace-object prerequisite for both negative
jobs. It does not grant `CAN_RUN`, `CAN_MANAGE`, Unity Catalog privileges,
group membership, storage credential/external-location access, or AWS
S3/KMS/IAM access.

The static validator requires exactly one matching `CAN_VIEW` entry. Three
regression tests prove it fails closed when the entry is removed or elevated
to `CAN_RUN` or `CAN_MANAGE`.

## Offline verification

Completed on `2026-08-11` without a connected command or cloud operation:

| Gate | Result |
| --- | --- |
| Goal 4 deterministic static validator | PASS |
| Goal 4 focused regression tests | PASS — 22 tests |
| Full offline pytest suite | PASS — 40 tests |
| Branch coverage | PASS — 96.67%, threshold 90% |
| Bundle/resource YAML parsing | PASS |
| Ruff format and lint | PASS — 69 files |
| Strict mypy | PASS — 5 source files |
| Bandit | PASS |
| detect-secrets over remediation files | PASS |
| ADR, artifact, merge-marker, and diff hygiene | PASS |

`pip-audit` is not rerun because this offline remediation changes no dependency
or lock file.

Reviewed source hashes after remediation:

- aggregate bundle source SHA-256:
  `26a6b65951f39e5bf9dcdb53f21d5ddc9c493d0346d60e3b68657e5f576508c1`;
- `databricks.yml` SHA-256:
  `4f8f038137ba72bc955493b77fa08ec1bbb9469a04b02228b4bdb8f286d176b5`;
- unchanged resource manifest SHA-256:
  `8ce89a428d0521344b279a767afaf02051fcdffaeae85ea2f13662745505f919`;
- unchanged protected-table SQL SHA-256:
  `23f27513b1ca110be0b093503d0112b33cfa4a22e80af2403092229ebb71c902`;
- unchanged direct-path SQL SHA-256:
  `f1a7ded07cefdc5e4a97e05c5368be3e6aba38a7d6704e4e652b010382416c8e`.

## Next approval boundaries

The separately approved strict connected validation used target `development`,
profile `ask-david-development`, the reviewed Terraform-derived variables, and
no `workspace_host` variable. Databricks CLI exited `0` with `Validation OK!`,
no warning, error, or recommendation for aggregate source SHA-256
`26a6b65951f39e5bf9dcdb53f21d5ddc9c493d0346d60e3b68657e5f576508c1`,
`databricks.yml` SHA-256
`4f8f038137ba72bc955493b77fa08ec1bbb9469a04b02228b4bdb8f286d176b5`,
and resource-manifest SHA-256
`8ce89a428d0521344b279a767afaf02051fcdffaeae85ea2f13662745505f919`.
No deployment, job/SQL run, data mutation, compute creation, Terraform, or AWS
operation occurred.

Remaining boundaries:

1. request separate exact-source redeployment approval;
2. inspect permissions and deployed negative SQL files read-only;
3. request a separate one-shot protected-table retry.

The direct-path negative job remains unexecuted until the protected-table test
produces the exact expected Unity Catalog authorization error.

## References

- [Databricks bundle permissions](https://docs.databricks.com/aws/en/dev-tools/bundles/permissions)
- [Databricks workspace access-control lists](https://docs.databricks.com/aws/en/security/auth/access-control)
