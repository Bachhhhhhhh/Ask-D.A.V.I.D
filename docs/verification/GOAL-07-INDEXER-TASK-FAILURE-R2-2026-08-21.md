# Goal 7 indexer task failure — ECR/S3 pull path — 2026-08-21

## Status

**TASK FAILED BEFORE CONTAINER START — NO RETRY**

After the approved workload-to-interface-endpoint TCP/443 egress rule was
applied, read-only preflight passed and exactly one private Goal 7 indexer task
was submitted. The task failed while pulling the digest-pinned image; the
container never started.

## Task evidence

- cluster: `ask-david-development-cluster`
- task definition: `ask-david-development-goal7-indexer:1`
- task ARN:
  `arn:aws:ecs:ap-southeast-1:736956442295:task/ask-david-development-cluster/70508306c3394c74b653bf5f15ab70cc`
- image digest:
  `sha256:c854fe57c92ad16be5cdb9935cfa16736164749a9812c9183157ad9417fae84f`
- network: private application subnet `subnet-0a1aad220d82ef879`,
  workload SG `sg-0a22126b47d3a5aea`, `assignPublicIp=DISABLED`
- task ENI: `eni-0dc879884a842ccb8`, private IP `10.42.42.10` (deleted after
  failed placement)
- final status: `STOPPED`
- stop code: `TaskFailedToStart`
- `StartedAt`: null
- container exit code: none
- log stream: none

The recorded failure was:

```text
CannotPullContainerError ... failed to do request: Get
...langgraph-runtime@sha256:c854...: dial tcp 52.219.124.111:443: i/o timeout
```

No retry, task override, ECR mutation, AOSS index mutation, Databricks
operation, Terraform operation, or additional AWS mutation occurred.

## Read-only network evidence

- ECR image digest exists in the private repository with immutable tag
  `goal7-runtime-17a425d0`.
- ECR API and DKR interface endpoints are `available`, private DNS enabled,
  present in both application subnets, and use endpoint SG
  `sg-09df4c29eba7991fa`.
- Endpoint SG ingress from workload SG TCP/443 exists.
- The applied workload egress rule to the interface-endpoint SG exists and is
  SG-scoped TCP/443.
- The private route table has an active S3 gateway endpoint route through
  `vpce-02706a3f82c187138` and managed prefix list `pl-6fa54006`.
- Workload SG egress inspection shows only the interface-endpoint SG TCP/443
  rule; no egress rule targets the S3 managed prefix list or a public CIDR.

## Current conclusion

The Secrets Manager endpoint blocker is remediated, but the image pull now
fails on the ECR layer/object path, which resolves to `52.219.124.111:443`.
The deterministic next hypothesis is that the workload SG needs a narrowly
scoped TCP/443 egress rule to the existing S3 gateway endpoint's managed prefix
list. This is only a diagnosis/design input; no such rule has been added.

## Next approval boundary

An offline source/test/documentation remediation must be reviewed first. Any
connected plan must be a new saved plan whose expected action is limited to the
S3-prefix-list egress path, with zero replacement/destroy/public/production or
unrelated actions. A new task run requires separate approval and must not be
implicitly retried from this failed execution.
