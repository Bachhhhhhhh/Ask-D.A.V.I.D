# Goal 7 indexer task failure — Databricks OAuth network path — 2026-08-21

## Status

**TASK STARTED, THEN FAILED — NO RETRY**

The separately approved one-shot private indexer run used the dedicated
revision `:2` image and reached `RUNNING`. It stopped with exit code `1`
before reading the governed outbox or touching AOSS. No retry was performed.

## Task evidence

| Item | Value |
| --- | --- |
| Cluster | `ask-david-development-cluster` |
| Task definition | `ask-david-development-goal7-indexer:2` |
| Task ARN | `arn:aws:ecs:ap-southeast-1:736956442295:task/ask-david-development-cluster/850ed5c9a2804d51bdf6af0d2c7fe5e0` |
| Image digest | `sha256:08ef16bfbd3e4dbd6a940227a6fd7afab14385644eec617d02da7c8f46714669` |
| Placement | Private application subnets; workload SG `sg-0a22126b47d3a5aea`; public IP disabled |
| Task ENI private IP | `10.42.46.195` |
| Started | `2026-08-21T01:39:38.306+07:00` |
| Stopped | `2026-08-21T01:41:32.220+07:00` |
| Stop code | `EssentialContainerExited` |
| Container exit | `1` |

## CloudWatch evidence

Stream:
`goal7-indexer/goal7-indexer/850ed5c9a2804d51bdf6af0d2c7fe5e0`

The sanitized stack trace shows `DatabricksSqlClient._token()` timing out
while connecting to the Databricks workspace OAuth endpoint. The entry point
then fails closed with:

```text
RuntimeError: Databricks OAuth token request failed
```

This occurs before `read_outbox()`, `ensure_index()`, `bulk_upsert()`, query
embedding, or AOSS search. There is therefore no evidence of an AOSS index or
document mutation from this run.

## Network interpretation

The task's private image-layer path and AWS endpoint path were previously
fixed. The current workload SG egress is limited to the AWS interface-endpoint
SG and the S3 gateway prefix list. It has no reviewed egress path to the
Databricks workspace OAuth endpoint. This run establishes a Databricks
workspace reachability blocker; it does not justify adding a broad public
CIDR rule or adding credentials to the image.

## What did not occur

- no retry or second ECS task;
- no Terraform plan/apply/destroy;
- no ECR push or image change;
- no Databricks SQL/bundle operation;
- no AOSS index/document mutation;
- no public IP or public network exposure.

## Next approval boundary

Perform an offline-only network-path analysis and minimal declarative
remediation design for private ECS-to-Databricks workspace access. The design
must preserve private task placement, avoid broad `0.0.0.0/0` egress, avoid
static credentials, and identify whether an existing approved NAT/PrivateLink
path can be used. Any Terraform source change, connected plan/apply, or task
retry requires its own approval.
