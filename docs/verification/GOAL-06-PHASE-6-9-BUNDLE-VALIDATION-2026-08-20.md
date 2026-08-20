# Goal 6 Phase 6-9 strict bundle validation

Date: `2026-08-20`

Status: `PASS — VALIDATED ONLY; NOT DEPLOYED OR RUN`

## Scope

Exactly one strict connected `databricks bundle validate` was run from the
`databricks/` bundle root against target `development` using profile
`ask-david-development`. The workspace profile resolved to workspace
`7474644358733471` in the approved development environment. No
`workspace_host` variable was supplied; authentication came from the named
profile.

The validation used the existing Serverless SQL Warehouse
`757e0335c6efb51e`, the Terraform-derived development catalog and S3 URIs,
workflow service principal
`b2bdec62-62db-432d-bc6f-1f92b78053b0`, denied-test service principal
`e06d5a6f-84f7-4dee-89a9-028c8541db8b`, and governance administrator from the
ignored development inputs. The denied path remained inside the approved
managed-storage prefix.

## Result

The CLI returned:

```text
Name: ask-david-goal-04-lakehouse
Target: development
Workspace:
  User: bachvxuan@gmail.com
  Path: /Workspace/Users/bachvxuan@gmail.com/.bundle/ask-david-goal-04-lakehouse/development

Validation OK!
```

There were no warnings, errors, or recommendations.

## Source hashes

| Source | SHA-256 |
| --- | --- |
| `databricks/databricks.yml` | `919901ef454b30a187a3fb65eee3a5dd7e14deaafa39850b91cba32869d60703` |
| `databricks/bundles/goal_06_doris/resources.yml` | `b88d73b70b84a8b9044eeeb9a6341b0f55cd5ab449f2f4b5b3b5caf8c9ff9e70` |
| `databricks/sql/goal_06/01_apply_controlled_increment.sql` | `4ac96983c0070172ce5286d021729d4e08baf804b92d667904f293eda204ad0d` |
| `databricks/sql/goal_06/02_verify_controlled_increment.sql` | `42a06c10d5829ecdccfd163f47c49675e1b49d0685244db2952f47f0d2deefff` |

## Boundary

No bundle deployment, job/SQL execution, table/data mutation, compute
creation, Terraform plan/apply/destroy, AWS operation, or ECS task occurred.
The next approval boundaries are separately:

1. deploy the reviewed bundle source set;
2. run the one-shot controlled increment job;
3. run the separately approved Doris refresh and comparison;
4. execute the disposable serving-copy rebuild only if required by the
   approved Phase 6-10 sequence; and
5. perform Phase 6-14 zero-drift and cleanup evidence.

Phase 6-9 is not complete from validation alone.
