# Goal 6 private admin-refresh revision-4 attempt — FE listener still unavailable

Date: 2026-08-13
Environment: development only (`736956442295`, `ap-southeast-1`)
Scope: one approved private task and read-only evidence

## Pre-run health inspection

Before the task run, read-only inspection confirmed:

- FE `i-01415e2378d0e2ca8` and BE `i-0e17d80269bc0f208` were `running` with
  EC2 system and instance checks `ok`;
- FE private IP `10.42.78.72`; BE private IP `10.42.73.187`;
- both hosts were in private subnet `subnet-09bc95f43115dca3e` with no public
  IP;
- task definitions revision `4` were `ACTIVE`, Fargate `awsvpc`, `512` CPU /
  `1024` MiB, and used the exact digest-pinned verifier image;
- no Goal 6 task was running before launch.

## Approved one-time execution

Exactly one admin-refresh task was launched with revision `4`:

```text
arn:aws:ecs:ap-southeast-1:736956442295:task/ask-david-development-cluster/1a02ebfc8f124cf787366bd032046973
```

Execution parameters were private application subnets
`subnet-034f5f1c9bca753f1` and `subnet-0a1aad220d82ef879`, security group
`sg-07a0dd2e8af8aa178`, Fargate `awsvpc`, and `assignPublicIp=DISABLED`.
The task ENI was `eni-031c9a63dfca62ed8`, private IP `10.42.46.3`, in
`subnet-0a1aad220d82ef879`.

No retry, second launch, Terraform operation, ECR operation, or out-of-band
repair occurred.

## Result

| Evidence | Result |
| --- | --- |
| Task terminal state | `STOPPED`, `EssentialContainerExited` |
| Container exit code | `1` |
| Completion marker | **MISSING** |
| Sanitized CloudWatch error | `ERROR 2002 (HY000): Can't connect to server on '10.42.78.72' (115)` |
| Private task attachment | PASS — private ENI/subnet, no public IP |

The task reached the private network and failed at the Doris FE connection.
The new revision did not produce the required `admin-refresh completed` marker.
This does not prove Unity Catalog/Iceberg interoperability, source refresh,
serving-mart behavior, or rebuildability.

## Stop condition

Per the Goal 6 failure policy, the task was not retried. The blocker remains
**Doris FE query-port/process readiness unverified or unavailable** despite
passing EC2 platform checks and the declarative Docker discovery/readiness
remediation. A new offline declarative diagnosis/remediation and a separately
reviewed saved plan are required before any further task run or infrastructure
mutation.
