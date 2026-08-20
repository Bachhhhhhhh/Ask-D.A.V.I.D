# Goal 6 Phase 6-14 — zero-drift and cleanup evidence

Date: 2026-08-20
Environment: development
AWS account: `736956442295`
AWS region: `ap-southeast-1`

## Scope and approval boundary

This checkpoint used the approved connected read-only development Terraform
plan and read-only ECS inspection. It did not apply, destroy, register a new
task definition, run an ECS task, change Doris data, or perform a Databricks
mutation. The Phase 6-10 disposable serving-copy rebuild was not executed in
this checkpoint and remains a separate approval boundary.

## Terraform zero-drift plan

The plan was created with the existing isolated provider cache and a separate
`TF_DATA_DIR`, so the repository's permission-owned `.terraform` directory was
not modified:

```text
TF_DATA_DIR=/tmp/goal6-connected-tfdata \
terraform -chdir=infrastructure/environments/development plan \
  -input=false -detailed-exitcode \
  -out=/tmp/goal6-phase6-14-zero-drift-20260820.tfplan
```

Result: **PASS** — Terraform returned `No changes` and exit `0` after
refreshing the approved AWS and Databricks development state. The saved local
plan SHA-256 is:

```text
2bbcb832f1c7929749062c3645705196e62a77d77f4ef184641d4206beadd4d5
```

The local JSON inspection reported `261` `no-op` resource changes and an
empty non-no-op list. There were zero creates, updates, replacements, and
destroys. The plan is an ignored local artifact and is not a repository
deliverable.

## Temporary-task cleanup inspection

Read-only ECS inspection of `ask-david-development-cluster` found no task in
`RUNNING` state. The two post-increment tasks were stopped successfully:

| Operation | Task | Definition | Exit | Result |
| --- | --- | --- | ---: | --- |
| Admin refresh | `b3314db778e84f47a5bdddaabdd599f0` | `ask-david-development-doris-admin-refresh:16` | 0 | `EssentialContainerExited` |
| Read-only verify | `9e399737d999478d9f8713d13b2485be` | `ask-david-development-doris-verifier:16` | 0 | `EssentialContainerExited` |

Read-only task-definition inspection confirmed both revision `16` families
remain `ACTIVE`, Fargate `awsvpc`, and use the approved audit-guard image
digest. No retry task was launched.

## Persistent and cost-bearing Goal 6 inventory

The following persistent resources remain intentionally deployed for the
development serving layer; Phase 6-14 does not destroy them:

- FE: `i-0959fcc02513accb6`, `m7i.xlarge`, private `10.42.64.238`, encrypted
  gp3 root `vol-0f3ac4e1a35b2d744` (30 GiB) and encrypted gp3 data
  `vol-0e8c9175fe79619be` (20 GiB).
- BE: `i-00ee935abe7df116f`, `m7i.xlarge`, private `10.42.71.97`, encrypted
  gp3 root `vol-0cdb0db2c141df1b8` (30 GiB) and encrypted gp3 data
  `vol-0b4799bdf2215d397` (50 GiB).
- CloudWatch log group: `/ask-david-development/doris`, 30-day retention.
- Private ECR repository:
  `736956442295.dkr.ecr.ap-southeast-1.amazonaws.com/ask-david-development/doris-verifier`
  with scan-on-push enabled.
- The existing private networking, KMS, Secrets Manager, ECS cluster, and
  interface-endpoint resources remain Terraform-managed and unchanged by this
  checkpoint.

## Acceptance result

| Check | Result | Evidence |
| --- | --- | --- |
| Development Terraform plan has zero unexpected drift | **PASS** | Saved plan SHA-256 above; 261 `no-op`, zero non-no-op actions |
| No temporary Goal 6 task remains running | **PASS** | Read-only ECS `RUNNING` task list was `[]` |
| Post-increment admin refresh and verifier stopped cleanly | **PASS** | Task IDs and exit code `0` above |
| Persistent/cost-bearing serving resources documented | **PASS** | Inventory above and read-only EC2/EBS/ECR/Logs inspection |
| Phase 6-10 disposable serving-copy rebuild | **NOT RUN IN THIS CHECKPOINT** | Requires its own approved operation |

This is durable Phase 6-14 zero-drift/cleanup evidence for the current
deployment state. It is not an overall Goal 6 completion claim: after the
separately approved Phase 6-10 rebuild, the required admin refresh and
read-only comparison must be rerun, followed by a new final zero-drift check.
