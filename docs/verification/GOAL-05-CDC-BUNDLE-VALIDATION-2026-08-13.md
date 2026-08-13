# Goal 5 corrected CDC bundle validation

Date: 2026-08-13
Scope: one approved strict connected Databricks bundle validation after the
offline CDC SQL remediation. No deployment, job/SQL execution, table/data
mutation, compute creation, Terraform operation, or AWS operation was
authorized or performed.

## Revalidation

| Check | Result | Evidence |
| --- | --- | --- |
| Specification | PASS | Goal 5 specification attachment was read completely before the connected step. |
| Source aggregate | PASS | `bd4cd49ee07147f9f240a10b936c78dad76b9dca62622b10f0fb62f6318eb3cd`; corrected CDC SQL hash `9ce80b73ec48bf0a7568fad81faf791f286dbfbae4c66ca0a9af84fe013f66fd`. |
| Databricks identity | PASS | Profile `ask-david-development`; authenticated principal `bachvxuan@gmail.com`; workspace ID `7474644358733471`. |
| AWS identity | PASS | Account `736956442295`; approved region `ap-southeast-1`. |
| Existing warehouse | PASS | `757e0335c6efb51e`, `Serverless Starter Warehouse`, Small/PRO, serverless enabled, `STOPPED`, auto-stop 10 minutes. |
| Workspace-host handling | PASS | Named profile authentication was used; no `workspace_host` bundle variable was supplied. |

## Exact validation

The single approved command ran from `databricks/` with target
`development`, profile `ask-david-development`, the reviewed Terraform-derived
warehouse, catalog, service-principal, governance-user, managed-storage probe,
and three Goal 5 source URI variables. Contract versions used their reviewed
bundle defaults.

Result:

```text
Name: ask-david-goal-04-lakehouse
Target: development
Workspace:
  User: bachvxuan@gmail.com
  Path: /Workspace/Users/bachvxuan@gmail.com/.bundle/ask-david-goal-04-lakehouse/development

Validation OK!
```

Strict mode returned exit `0` with no warning, error, or recommendation. The
local output artifact is `/tmp/goal5-cdc-remediation-strict-bundle-validate-20260813.log`.

## Boundary and next checkpoint

This validates only the corrected bundle configuration. It does not prove that
the corrected SQL has been deployed or executed. The next separately approved
step is redeployment of the exact corrected source set, with immediate
read-only inspection and no job/SQL run. A further separate approval is
required for one CDC workflow retry, followed by output, idempotency,
provenance, quality, and authoritative Tables API verification.

Goal 5 remains unverified until those connected execution and evidence
checkpoints pass.
