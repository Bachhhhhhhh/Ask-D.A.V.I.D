# Goal 7 indexer task failure — AOSS vector upsert

## Approved execution boundary

Exactly one private, no-retry ECS task was run from
`ask-david-development-goal7-indexer:3` in account `736956442295`, region
`ap-southeast-1`, cluster `ask-david-development-cluster`. It used private
application subnets `subnet-034f5f1c9bca753f1` and
`subnet-0a1aad220d82ef879`, dedicated Goal 7 SG `sg-0ff2bcb1d5175c931`, and
`assignPublicIp=DISABLED`.

Task ARN:

`arn:aws:ecs:ap-southeast-1:736956442295:task/ask-david-development-cluster/1b2498bb442345b784f50da54e84fd49`

## Result

- Task definition: revision `3`
- Image digest:
  `sha256:56263b9c594825f1509f305bb9911b499acd944dcc9971731d04dc18b530a641`
- Task status: `STOPPED`
- Stop code: `EssentialContainerExited`
- Container exit code: `1`
- No retry was run.

CloudWatch stream
`goal7-indexer/goal7-indexer/1b2498bb442345b784f50da54e84fd49` contains the
bounded traceback ending at:

```text
File "/app/ask_david_goal7/indexer.py", line 362, in bulk_upsert
    raise RuntimeError("AOSS vector upsert failed")
RuntimeError: AOSS vector upsert failed
```

This proves the corrected image passed startup and reached the AOSS bulk
upsert path. It does not prove that the vector upsert succeeded or that the
complete index/search contract passed. The response status/body was not
emitted by the current runtime, so the precise AOSS rejection is not yet
independently identifiable from the durable task log.

The task ENI was `eni-02843a2a8fce425ea`; immediate post-stop inspection found
that AWS had already removed it (`InvalidNetworkInterfaceID.NotFound`), so no
private-IP claim is made.

## Boundary and next action

No retry, new task, Terraform operation, ECR push, Databricks operation, or
additional AOSS operation was performed after the failure. Goal 7 remains
**UNVERIFIED**. The next step requires an offline source/log analysis and a
minimal remediation design to expose the bounded AOSS failure response without
weakening security or broadening scope, followed by separate approval before
any new image/task or connected operation.
