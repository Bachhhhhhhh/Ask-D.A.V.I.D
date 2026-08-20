# Goal 6 private admin-refresh revision-3 attempt — FE connectivity blocker

Date: 2026-08-13
Environment: development only (`736956442295`, `ap-southeast-1`)
Task definition: `ask-david-development-doris-admin-refresh:3`
Image digest: `sha256:d51145436a95ba7e2b553411e9036362122b14dc201f9ebc8e06b45d852196d6`

## Approved execution

After the MariaDB-compatible image and revision-3 task-definition apply were
reviewed, exactly one private admin-refresh task was launched. The host has no
PowerShell runtime, so the repository wrapper's fail-closed guards were
reproduced before the equivalent single ECS control-plane request. No second
launch or retry was made.

| Field | Evidence |
| --- | --- |
| Cluster | `ask-david-development-cluster` |
| Task ARN | `arn:aws:ecs:ap-southeast-1:736956442295:task/ask-david-development-cluster/ebb2e643d9bd435ab4245d2645dc8a14` |
| Launch type | Fargate, `awsvpc`, `assignPublicIp=DISABLED` |
| Security group | `sg-07a0dd2e8af8aa178` (Goal 6 admin task) |
| ENI | `eni-019ed59340a8e1d92` |
| Private subnet / IPv4 | `subnet-0a1aad220d82ef879` / `10.42.35.84` |
| FE target rendered by task definition | `10.42.76.67:9030` |

## Result

The task reached `STOPPED` with `stopCode=EssentialContainerExited` and
container exit code `1`. The required non-sensitive completion marker was not
emitted. Sanitized CloudWatch inspection returned only:

```text
ERROR 2002 (HY000): Can't connect to server on '10.42.76.67' (115)
```

No secret, token, password, or raw task output was recorded. The private ENI
attachment is correct, but this attempt does not prove that the FE listener is
healthy or that the admin refresh reached Doris.

## Stop condition

Per the Goal 6 failure policy, no retry, task mutation, Terraform operation,
security-group change, instance change, or out-of-band repair was performed.
Doris health, Unity Catalog interoperability, source refresh, serving-mart
behavior, and rebuildability remain unverified.

## Read-only diagnosis

A separately approved diagnosis inspected the current AWS state without
running a host command, task, or mutation:

- FE `i-074e456efa350b444` is `running`, has EC2 system/instance checks `ok`,
  private IP `10.42.76.67`, and no public IP. The replacement BE
  `i-0118ff6e619268859` is likewise running/private with passing EC2 checks.
- The admin egress rule `sgr-0eedebb0bc56901c2` allows TCP/9030 from
  `sg-07a0dd2e8af8aa178` to FE SG `sg-019b900ee5601c208`; the matching FE
  ingress rule is `sgr-0e99246fa49b722e5`. Both peer IDs are in account
  `736956442295`.
- The verifier subnet and FE subnet share VPC `vpc-007ba758b98a9ab9e`; the
  route table has an active local `10.42.0.0/16` route, and the associated
  network ACL allows all traffic at rule 100 in both directions.
- VPC Flow Logs are active and delivered successfully. Matching records for
  the failed task show repeated TCP packets from `10.42.35.84` to
  `10.42.76.67:9030` with action `ACCEPT`, followed by packets from the FE
  address back to the task with action `ACCEPT`; no matching `REJECT` record
  exists. The 60-byte client packets and 40-byte FE responses are consistent
  with an active refusal/no listener, not a dropped SG/NACL path.
- Sanitized FE/BE EC2 console output shows cloud-init finished and Docker
  successfully pulled and launched the pinned FE/BE images. It does not prove
  that the Doris FE process remained alive or bound to 9030. The Doris log
  group contains no FE/BE application stream, so a process-level root cause
  cannot be recovered from the approved read-only evidence.

## Diagnosis and stop condition

The exact blocker is now narrowed to **FE query-port listener/process
unavailability**. The private network path is not the blocker. The process
root cause remains unverified because no approved SSM/host shell or second ECS
task may be used for diagnosis. No retry, task mutation, Terraform operation,
security-group change, instance change, or out-of-band repair was performed.

Any repair must be implemented declaratively, validated offline, and reviewed
in a new saved Terraform plan before mutation. Until then, Doris health, Unity
Catalog interoperability, source refresh, serving-mart behavior, and
rebuildability remain unverified.
