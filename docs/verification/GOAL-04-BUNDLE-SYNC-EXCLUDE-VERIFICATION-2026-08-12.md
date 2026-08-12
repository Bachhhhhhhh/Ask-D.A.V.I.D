# Goal 4 bundle sync exclusion verification

## Scope

This report records the separately approved redeployment of the exact Goal 4
development bundle source aggregate:

`49730c2fe6ccc38d15bc9511f626e17992d088eb4ced45eb745c22ff80769027`

The approved scope was limited to applying the `sync.exclude` remediation and
performing immediate read-only inspection. No job or SQL run, compute
creation, Terraform operation, or AWS operation was authorized or performed.

## Deployment evidence

- Profile: `ask-david-development`
- Target: `development`
- Databricks workspace: `7474644358733471`
- Databricks CLI: `1.11.0`
- Result: `Deployment complete!`, exit `0`
- Offline Goal 4 static validation: PASS before deployment

The read-only bundle summary reports the exact synchronization boundary:

```yaml
sync:
  include:
    - sql/goal_04/*.sql
  exclude:
    - sql/goal_04/remediation/**
```

The summary still resolves exactly the existing five Goal 4 jobs:

| Job | ID | Warehouse | Tasks |
| --- | ---: | --- | ---: |
| Synthetic managed-Iceberg pipeline | `967410491586823` | `757e0335c6efb51e` | 8 |
| Managed-Iceberg history verification | `695423086105630` | `757e0335c6efb51e` | 1 |
| Lineage verification | `825751066015430` | `757e0335c6efb51e` | 1 |
| Denied table-access verification | `187789722076444` | `757e0335c6efb51e` | 1 |
| Denied direct-path verification | `992194321630936` | `757e0335c6efb51e` | 1 |

## Workspace file inspection

The read-only workspace listing contains exactly 13 top-level files under:

`/Workspace/Users/bachvxuan@gmail.com/.bundle/ask-david-goal-04-lakehouse/development/files/sql/goal_04`

The excluded path:

`.../files/sql/goal_04/remediation`

does not exist. Therefore the previously leaked destructive remediation file
is absent from the deployed workspace. No ad-hoc workspace deletion was used.

No job, SQL task, table mutation, Terraform operation, AWS operation, or
additional compute was run in this checkpoint. The repository working tree
remains intentionally uncommitted and contains the pre-existing Goal 4
change set.

## Result

| Check | Result |
| --- | --- |
| Exact source aggregate matched | PASS |
| Deployment completed | PASS |
| Explicit `sync.exclude` present in deployed summary | PASS |
| Excluded remediation file absent | PASS |
| Five existing jobs retained | PASS |
| Job/SQL execution | NOT RUN by scope |
| Table format | Read-only inventory remains managed Delta UniForm with Iceberg-compatible metadata; native Iceberg is not claimed |

This resolves the bundle-sync blocker. Under the approved development
compatibility profile, the existing managed Delta UniForm tables are retained;
final Goal 4 verification still requires refreshed read-only resource
inspection, zero-drift evidence, offline gates, and an immutable evidence
commit. Native Iceberg is not claimed.
