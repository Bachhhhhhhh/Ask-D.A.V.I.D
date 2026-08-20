# Goal 6 FE listener remediation — connected saved plan

Date: 2026-08-13
Environment: development only (`736956442295`, `ap-southeast-1`)
Phase: connected read-only refresh and saved-plan review; **no apply**

## Revalidation

| Prerequisite | Result |
| --- | --- |
| AWS identity/account | PASS — `arn:aws:iam::736956442295:user/bach_dev_admin_david` |
| AWS region | PASS — `ap-southeast-1` |
| Databricks workspace read-only refresh | PASS — workspace `7474644358733471`; metastore `3a7f7e7a-680b-4bd6-907a-6d5e77b43178`; SQL warehouse `757e0335c6efb51e` |
| Development-only gates | PASS — `goal_6_enabled=true`; no production input |
| Mutation performed | NONE — Terraform only refreshed remote state and wrote a local saved plan |

## Saved artifact

Ignored local artifact:

```text
infrastructure/environments/development/goal-06-fe-listener-remediation-20260813.tfplan
```

SHA-256:

```text
90c504a9e54529d3d4d82e61088455573ab0d02d9ff287df47bc0b6ca7bf83a0
```

The plan was created with the approved Terraform development backend and a
read-only remote-state refresh. No `terraform apply`, `destroy`, ECS task,
ECR push, Databricks mutation, SQL/job run, or bundle operation occurred.

## Exact action set

The JSON plan contains **243 no-op resources** and **six delete/create
replacements** (`6 to add, 0 to change, 6 to destroy` in Terraform's summary):

| Terraform address | Replacement trigger | Reviewed effect |
| --- | --- | --- |
| `module.doris_serving.aws_instance.fe[0]` | `user_data` | Re-bootstrap private FE with `FE_SERVERS`, `FE_ID`, private listener readiness guard, and generation `2`; no public IP or topology change |
| `module.doris_serving.aws_instance.be[0]` | `user_data` | Re-bootstrap private BE with `FE_SERVERS`, `BE_ADDR`, private listener readiness guard, and generation `2`; no public IP or topology change |
| `module.doris_serving.aws_volume_attachment.fe[0]` | `instance_id` | Detach/reattach the existing FE metadata volume to the replacement FE |
| `module.doris_serving.aws_volume_attachment.be[0]` | `instance_id` | Detach/reattach the existing BE serving-data volume `vol-01e9b0ed05f7b92b9` to the replacement BE; the volume itself is not deleted |
| `module.doris_verifier.aws_ecs_task_definition.admin[0]` | `container_definitions` | Register a new revision because the FE/BE private IP inputs become unknown while the hosts are replaced |
| `module.doris_verifier.aws_ecs_task_definition.verifier[0]` | `container_definitions` | Register a new revision because the FE private IP input becomes unknown while the FE is replaced |

The two ECS task-definition replacements are derived from the host replacement:
their container definitions embed the Terraform-derived private FE/BE
addresses. They are not task runs, services, IAM changes, network changes, or
public exposure. They are nevertheless additional replacements beyond the
four host/attachment replacements and must be accepted explicitly before any
apply.

No standalone EBS-volume deletion, IAM/KMS change, security-group/route/NACL
change, S3/source-data change, Databricks resource change, ECR change,
production change, or public ingress appears in the plan.

## Review result and boundary

The plan is valid for review and is **not applied**. The action set is larger
than the narrow FE/BE-plus-attachment expectation in the offline report because
the two Terraform-managed verifier task definitions depend on the replaced
private IP outputs. Applying it requires a separate hash-bound approval that
names all six replacements above. If that derived task-definition replacement
is not accepted, stop and create a declarative correction and a fresh plan;
do not apply this artifact or repair the task definitions out of band.

## Evidence commands

- `aws sts get-caller-identity --query '{Account:Account,Arn:Arn}'`
- Terraform `init -reconfigure -backend-config=backend.hcl`
- Terraform `plan -refresh=true -out=goal-06-fe-listener-remediation-20260813.tfplan`
- Terraform `show -json` action-count and address review
- `sha256sum infrastructure/environments/development/goal-06-fe-listener-remediation-20260813.tfplan`

The artifact is Git-ignored and must never be committed.
