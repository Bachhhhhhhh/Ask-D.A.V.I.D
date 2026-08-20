# Goal 6 Phase 6-4 connected foundation plan

Date: 2026-08-13
Environment: development only (`736956442295`, `ap-southeast-1`)
Phase: saved-plan review; no apply

## Read-only revalidation

| Prerequisite | Result |
| --- | --- |
| AWS caller identity | PASS — account `736956442295`, approved development administrator identity |
| AWS region | PASS — `ap-southeast-1` in the reviewed backend and development inputs |
| Databricks workspace profile | PASS — `ask-david-development` authenticated to workspace `7474644358733471` |
| Unity Catalog metastore | PASS — workspace is attached to `3a7f7e7a-680b-4bd6-907a-6d5e77b43178` |
| Existing SQL warehouse | PASS — approved Serverless Starter Warehouse `757e0335c6efb51e`; no warehouse change is planned |
| Foundation gates | PASS — `goal_5_source_objects_enabled=true`, `goal_6_enabled=true`, and `goal_6_verifier_tasks_enabled=false` |

## Saved plan

Artifact (ignored by Git):
`infrastructure/environments/development/goal-06-foundation-remediated-20260813.tfplan`

SHA-256:

```text
71c98b16a8531ac49a64cd789933e174c207cf610d28e74a39cd8347f6ebbddc
```

Terraform refresh read the remote state and then created this local artifact.
It did not apply, destroy, replace, push an image, deploy a bundle, run SQL, or
run an ECS task.

| Action | Count |
| --- | ---: |
| Create | 47 |
| Update in place | 3 |
| Replace | 0 |
| Destroy | 0 |
| Read data source | 1 |
| No-op managed objects | 195 |

The three in-place updates are the Unity Catalog catalog grant, the
`green_sm_business` schema grant, and the existing observability KMS key policy.
They add the dedicated, least-privilege Goal 6 external-read path and the
narrow CloudWatch Logs permission. There is no metastore, workspace assignment,
SQL warehouse, cluster, production, or AWS Glue/HMS action.

## Reviewed creates

- Databricks: one dedicated Doris external-read service principal, its bounded
  secret, entitlement, workspace assignment, access-control rule set, and one
  allowlisted Business-table grant.
- Doris hosts: one private FE and one private BE, both `m7i.xlarge`, with
  encrypted `gp3` EBS volumes of 20 GiB and 50 GiB respectively; the instances
  use no public-IP setting in the declarative source.
- Private network: four security groups, seven security-group ingress rules
  limited to dedicated groups and documented Doris ports, and six narrowly
  defined egress rules. The only public-CIDR rules are private-subnet TCP/443
  egress through existing NAT; they have the reviewed resource-scoped Trivy
  annotations and are not ingress.
- Supporting AWS resources: immutable private verifier ECR repository,
  least-privilege instance/admin/verifier IAM roles and policies, three
  Secrets Manager containers and versions, KMS-encrypted Doris log group, and
  one SSE-KMS synthetic increment fixture object.

No `aws_ecs_task_definition` for Goal 6 is created. The three existing Goal 3
smoke task definitions and all three verified Goal 5 source objects are no-op.

## Cost-bearing resources if applied

- two persistent `m7i.xlarge` EC2 instances;
- 20 GiB and 50 GiB encrypted gp3 EBS volumes;
- CloudWatch Logs ingestion/retention, KMS requests, Secrets Manager, ECR, and
  normal private-NAT data processing.

The separately created ECR repository has no Goal 6 image at this phase. No
Fargate task definition or running task is part of this plan.

## Apply outcome

The exact artifact above was subsequently approved and applied, but the apply
stopped with partial Terraform-state ownership. The post-apply inventory and
the required remediation boundary are recorded in
`GOAL-06-PHASE-6-5-PARTIAL-APPLY-2026-08-13.md`. Do not reuse this saved plan.
