# Goal 4 bundle authentication and root-path remediation

## Scope and boundary

This report records the first strict connected bundle-validation failure and
the approved offline-only remediation. It does not authorize another connected
bundle validation, bundle deployment, job or SQL execution, Terraform
plan/apply/destroy, or AWS/Databricks mutation.

## Active-foundation prerequisite

The active-stage saved plan SHA-256
`c4a81b50ef40531b38a1f785f861d281db02b9e20bc391b209b4c906dafe8502`
applied successfully as `54 added, 1 changed, 0 destroyed`. Its reviewed AWS
action count was zero, and it contained no replacement, destroy,
metastore/assignment, warehouse/cluster, production, or Goal 5+ action.
Immediate read-only inspection verified the intended Databricks foundation;
the existing Serverless SQL warehouse remained stopped and no project cluster
existed.

## First failed strict validation evidence

Exactly one approved command attempted strict validation of the development
target with Databricks CLI `1.11.0` and profile
`ask-david-development`. It exited `1` before deployment because the bundle
defined `workspace.host: ${var.workspace_host}` and profile matching occurred
before that interpolation resolved. The CLI reported that the profile host did
not match the unresolved bundle host and also warned that it failed to parse
`https://${var.workspace_host}`.

Immediate inspection found no side effect:

- the existing warehouse remained `STOPPED`;
- no project cluster or active session existed;
- no Goal 4 job existed;
- no `databricks/.databricks` bundle state directory was created;
- no deployment, SQL run, Terraform operation, or AWS mutation occurred.

## Declarative remediation

The repository-managed bundle now:

- removes the `workspace_host` custom variable;
- removes all bundle and target `workspace.host` mappings;
- delegates workspace selection and OAuth authentication exclusively to the
  approved named CLI profile;
- scopes `workspace.root_path` to
  `/Workspace/Users/${var.governance_admin_user_name}/.bundle/${bundle.name}/${bundle.target}`;
- avoids `/Workspace/Shared`, whose top-level permissions can conflict with
  bundle permissions.

The deterministic static validator rejects reintroduction of an interpolated
workspace-host mapping, rejects `/Workspace/Shared`, and requires the exact
user-scoped root. Regression tests exercise both failure modes.

## Second failed strict validation evidence

After the first offline remediation passed, exactly one separately approved
strict connected validation ran with the same development target and named
profile. The host/profile failure was resolved. Validation exited `1` before
deployment because strict mode found one warning:

- the user-scoped workspace folder inherited `CAN_MANAGE` for
  `bachvxuan@gmail.com`, but that user permission was not declared in the
  bundle ACL.

The CLI also recommended putting `workspace.root_path` directly under the
production-mode target. No connected retry, deployment, job/SQL run, Terraform
operation, or AWS mutation followed. The command created only the ignored
local `databricks/.databricks/.gitignore`; it created no bundle deployment
state file.

The approved offline remediation now:

- moves the unchanged user-scoped root to
  `targets.development.workspace.root_path`;
- declares `user_name: ${var.governance_admin_user_name}` with
  `level: CAN_MANAGE`, matching rather than broadening the inherited user-folder
  permission;
- extends the deterministic validator and regression tests to reject a
  top-level-only root or missing governance-admin permission.

## Successful strict validation evidence

After the second offline remediation passed, exactly one separately approved
strict connected validation ran against bundle SHA-256
`a3c4d178fc44afe19691403dd3a746822e24f88e53782432f2f51f0ae6c394e7`
and resource-manifest SHA-256
`8ce89a428d0521344b279a767afaf02051fcdffaeae85ea2f13662745505f919`.
It used target `development`, profile `ask-david-development`, the existing
approved warehouse and Terraform-derived variables, and no `workspace_host`
variable.

Databricks CLI `1.11.0` exited `0` with `Validation OK!`, no warning, and no
recommendation. It resolved user `bachvxuan@gmail.com` and path
`/Workspace/Users/bachvxuan@gmail.com/.bundle/ask-david-goal-04-lakehouse/development`.

No bundle deployment, job/SQL run, compute creation, Terraform operation, or
AWS mutation was authorized or performed. Local bundle metadata still contains
only the ignored two-byte `databricks/.databricks/.gitignore`.

## Offline verification

Completed on `2026-08-11` without a connected command or cloud operation:

| Gate | Result |
| --- | --- |
| Goal 4 deterministic static validator | PASS |
| Bundle and resource YAML parsing | PASS |
| Bundle auth/root-path regression tests | PASS — 14 Goal 4 tests total |
| Full offline pytest suite | PASS — 32 tests |
| Branch coverage | PASS — 96.67%, threshold 90% |
| Ruff format check | PASS — 64 files |
| Ruff lint | PASS |
| Strict mypy | PASS — 5 source files |
| Bandit | PASS |
| detect-secrets hook over the remediation files | PASS |
| Merge-marker, tracked-sensitive-artifact, and `git diff --check` checks | PASS |

The repository `.venv` launchers and cache directories came from a previous
container path and ownership. Validation therefore invoked the already
installed Python packages through the current Python 3.12 interpreter and put
Ruff, mypy, pytest, and coverage caches/reports under `/tmp`; no dependency was
installed or updated. `pip-audit` was not rerun because this approval was
strictly offline and dependency-vulnerability lookup can require network
access. The same locked dependency set passed the preceding Goal 4 offline
gate; this remediation changes no dependency manifest or lock file.

## Next approval boundary

Strict connected bundle validation is complete. The next boundary is separate
approval to deploy the exact reviewed bundle and synchronized SQL file set.
Deployment may create or update only the five declared development jobs and
their workspace files; it must not run a job or SQL task, create compute,
execute Terraform, or mutate AWS. After deployment, perform read-only resource
inspection and stop before any workflow run.
