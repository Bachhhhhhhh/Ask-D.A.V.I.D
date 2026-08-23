# Goal 7 connected Terraform apply — 2026-08-21

## Status

**SAVED PLAN APPLIED — TASKS NOT RUN**

The exact hash-bound saved development plan was applied after explicit
approval. No ECS task was started, no OpenSearch index was created, no
Databricks SQL or bundle operation was run, and no unrelated resource was
mutated.

## Approval and identity

- AWS account: `736956442295`
- AWS region: `ap-southeast-1`
- AWS principal: `arn:aws:iam::736956442295:user/bach_dev_admin_david`
- applied plan SHA-256:
  `05b8bf41457d2093d0fc4230779b2e612fb120453c6b359e2d1e7e7a34309e31`
- plan artifact:
  `/tmp/goal7-connected-plan.cvxyDv/goal-07-development.tfplan`

The artifact hash was rechecked immediately before apply.

## Apply result

Terraform reported:

```text
Apply complete! Resources: 8 added, 0 changed, 0 destroyed.
```

The applied resources were exactly the eight reviewed creates:

- KMS-encrypted `goal7/workflow-oauth` secret container;
- workflow OAuth secret version;
- workflow service-principal secret;
- ECS execution-role read/decrypt policy;
- private indexer-to-AOSS TCP/443 rule;
- private demo-to-Doris-FE TCP/9030 rule;
- Goal 7 indexer task definition revision 1;
- Goal 7 integrated-demo task definition revision 1.

No replacement or destroy occurred.

## Immediate read-only inspection

| Check | Result |
| --- | --- |
| Indexer SG rule | PASS — `sgr-0a329564a6c599fdd`, workload SG to AOSS SG, TCP/443 |
| Integrated-demo SG rule | PASS — `sgr-0ec7bee8eada52b6e`, workload SG to Doris FE SG, TCP/9030 |
| Indexer task definition | PASS — family `ask-david-development-goal7-indexer`, revision 1, ACTIVE, Fargate |
| Integrated-demo task definition | PASS — family `ask-david-development-goal7-integrated-demo`, revision 1, ACTIVE, Fargate |
| Workflow secret metadata | PASS — KMS-backed, not deleted; secret value not read or printed |
| FE/BE private IPs | PASS — FE `10.42.64.238`, BE `10.42.71.97` |
| Existing Doris data volumes | PASS — preserved encrypted volumes remain attached; inspection caught transient `attaching` state |
| ECS task run | NOT RUN |
| AOSS index mutation | NOT RUN |
| Databricks SQL/bundle operation | NOT RUN |

The immediate EC2/volume inspection observed both Doris instances in
transient `pending` state and both preserved data-volume attachments in
transient `attaching` state. No action was taken; later readiness inspection
must be separately read-only.

## Current checkpoint

The Goal 7 private task-definition foundation is applied, but Goal 7 is not
verified. The next approval boundary is one read-only readiness/identity and
network inspection followed by a separately approved single private indexer
task run. The integrated demo task requires its own later approval. Do not
create the AOSS index or run either task implicitly.
