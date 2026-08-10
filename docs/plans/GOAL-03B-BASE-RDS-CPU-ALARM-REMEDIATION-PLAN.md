# Goal 3B base RDS CPU alarm remediation plan

**Status:** CONNECTED ACCEPTANCE PASS — DURABLE EVIDENCE COMMIT PENDING
**Scope:** Minimal remediation of the accepted Goal 3 observability contract
**AWS account/Region for any later connected checkpoint:**
`736956442295` / `ap-southeast-1`

The owner approved offline source implementation with a development threshold
of `90`. Terraform source, tests, the read-only runbook, and documentation are
implemented and validated offline. The exact reviewed Terraform remediation
was subsequently applied, passed read-only connected verification, and passed
the separately approved final zero-drift plan. The chronological approval and
verification evidence is recorded below.

## Problem statement

The approved Goal 3 plan assigns CloudWatch log groups, retention, base alarms,
an alert topic without subscriptions, and explicit alarm-threshold inputs to
the observability foundation. `docs/INFRASTRUCTURE.md` narrows the base alarm
to an RDS CPU alarm. At gap-discovery time, the Terraform tree and deployed
development state contained the log groups, VPC Flow Log, encrypted SNS topic,
and KMS key, but no `aws_cloudwatch_metric_alarm` or alarm-threshold input.

The final connected development plan exited `0`, proving that AWS matches the
current Terraform configuration. It does not close this gap because both AWS
and Terraform omit the accepted alarm scope.

## Objective

Add exactly one base alarm for sustained high average CPU utilization on the
Terraform-managed PostgreSQL RDS instance, using the existing encrypted SNS
alert topic as its only action. Preserve the accepted lack of SNS subscriptions
and all existing Goal 3 boundaries.

## Fixed design

### Alarm contract

| Property | Planned value |
| --- | --- |
| Terraform resource | `aws_cloudwatch_metric_alarm.rds_cpu_high` in the observability module |
| Alarm name | `${name_prefix}-rds-cpu-high` |
| Namespace / metric | `AWS/RDS` / `CPUUtilization` |
| Dimension | `DBInstanceIdentifier` set from the managed RDS resource output |
| Statistic / unit | `Average` / `Percent` |
| Comparison | `GreaterThanThreshold` |
| Period | 60 seconds |
| Evaluation periods | 5 |
| Datapoints to alarm | 5 |
| Threshold | Required environment input `rds_cpu_alarm_threshold_percent` |
| Missing data | `missing` |
| ALARM action | Existing encrypted `aws_sns_topic.alerts` ARN |
| OK / insufficient-data actions | None |
| Subscriptions | None; still deferred |

Amazon RDS publishes `CPUUtilization` in `AWS/RDS` with the
`DBInstanceIdentifier` dimension. AWS currently recommends average RDS CPU
monitoring with a 60-second period, five evaluation periods, five datapoints to
alarm, and a 90-percent reference threshold. The threshold remains a required
environment input because the approved project plan explicitly makes alarm
thresholds environment-specific.

Official references:

- [Amazon RDS CloudWatch metrics](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-metrics.html)
- [Viewing RDS metrics and dimensions](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/metrics_dimensions.html)
- [AWS recommended alarms for RDS](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Best_Practice_Recommended_Alarms_AWS_Services.html)
- [Terraform AWS metric-alarm resource](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_metric_alarm)

### Threshold input

Add a required numeric development-root variable and pass it into the
observability module:

```hcl
variable "rds_cpu_alarm_threshold_percent" {
  type = number

  validation {
    condition = (
      var.rds_cpu_alarm_threshold_percent > 0 &&
      var.rds_cpu_alarm_threshold_percent <= 100
    )
    error_message = "rds_cpu_alarm_threshold_percent must be greater than 0 and no greater than 100."
  }
}
```

The committed example and mock tests should use `90`. The ignored local
`infrastructure/environments/development/terraform.tfvars` must be updated by
the owner before a connected plan. The implementation must not invent or
silently default the real environment value.

### RDS identifier wiring

Expose `aws_db_instance.postgres.identifier` as
`rds_instance_identifier` from `modules/data-services`. Pass that typed output
into `modules/observability`; do not derive the dimension from an endpoint or
duplicate a naming convention in the development root.

### Encrypted SNS action and KMS policy

The existing SNS alert topic uses the customer-managed observability KMS key.
AWS requires an event-source service publishing into an encrypted SNS topic to
have `kms:GenerateDataKey*` and `kms:Decrypt`. Add one statement to the
observability key policy for `cloudwatch.amazonaws.com`, restricted by:

- `aws:SourceAccount` equal to the approved account input; and
- `aws:SourceArn` equal to the deterministic ARN of only
  `${name_prefix}-rds-cpu-high` in the configured Region.

Preserve the account-root administration statement and the existing regional
CloudWatch Logs statement scoped to the two approved log-group encryption
contexts. Do not grant broad CloudWatch access, do not add an SNS subscription,
and do not replace the existing KMS key.

Official reference:
[Managing Amazon SNS encryption keys](https://docs.aws.amazon.com/sns/latest/dg/sns-key-management.html).

No new SNS topic policy is planned for this same-account alarm. Cross-account
publishing remains out of scope. If a connected plan or AWS validation shows a
same-account topic-policy requirement, stop and review it as a scope change
instead of adding permissions opportunistically.

## Planned file changes

| File | Planned change |
| --- | --- |
| `infrastructure/modules/data-services/outputs.tf` | Export the managed RDS instance identifier. |
| `infrastructure/modules/observability/variables.tf` | Add the RDS identifier and CPU-threshold module inputs with validation. |
| `infrastructure/modules/observability/main.tf` | Add exactly one RDS CPU alarm wired to the existing alert topic. |
| `infrastructure/modules/observability/outputs.tf` | Export the alarm name for deterministic read-only verification. |
| `infrastructure/modules/observability/observability.tftest.hcl` | Assert metric, dimension, timing, threshold, missing-data behavior, SNS action, and no OK/insufficient-data actions. |
| `infrastructure/modules/kms/main.tf` | Add the exact-alarm CloudWatch publisher statement to the existing observability key policy. |
| `infrastructure/modules/kms/kms.tftest.hcl` | Assert the new principal/actions/conditions and regression-test the existing log-group restrictions. |
| `infrastructure/environments/development/variables.tf` | Add the required environment threshold input. |
| `infrastructure/environments/development/main.tf` | Wire the data-services identifier and threshold into observability. |
| `infrastructure/environments/development/outputs.tf` | Export the alarm name and existing alert-topic ARN for exact runbook verification. |
| `infrastructure/environments/development/tests/development.tftest.hcl` | Supply the test threshold and assert the root wiring. |
| `infrastructure/environments/development/terraform.tfvars.example` | Document the example value `90`. |
| `scripts/dev.py` and `tests/unit/test_infrastructure_preflight.py` | Require the explicit threshold during offline/connected preflight and regression-test omission. |
| `infrastructure/scripts/smoke.ps1` | Add read-only alarm discovery and exact contract checks; do not change alarm state or publish a message. |
| `infrastructure/README.md` and `docs/INFRASTRUCTURE.md` | Align the documented alarm contract, KMS requirement, threshold input, and validation boundary. |
| `docs/PROJECT_STATUS.md` and the Goal 3B verification report | Record implementation and verification evidence only after each checkpoint actually occurs. |

The ignored local development `terraform.tfvars` is an environment input, not
a committed file. Updating it is a manual prerequisite for later preflight and
connected planning.

## Explicit non-goals

- No additional alarm beyond the single RDS CPU alarm.
- No SNS email, SMS, HTTP, Lambda, SQS, or other subscription.
- No forced alarm-state transition or synthetic CPU load.
- No CloudWatch dashboard, composite alarm, anomaly detection, metric math,
  log metric filter, or application alarm.
- No RDS, Redis, networking, ECS, S3, OpenSearch, Databricks, agent, tool
  service, or business-data change.
- No change to Goal 4 or any later roadmap goal.

## Security and operational review

1. **KMS confused-deputy risk:** acceptable only with both exact source account
   and exact alarm ARN conditions. A service-principal-only grant is rejected.
2. **KMS lockout risk:** preserve and regression-test the account-root and
   CloudWatch Logs statements; no KMS key replacement is allowed.
3. **Notification exposure:** no subscriber is created, so no address or
   external endpoint enters Terraform or chat.
4. **Sensitive data:** alarm names, descriptions, tags, and actions must not
   contain credentials, database secrets, or business data.
5. **False positives:** use a sustained five-minute evaluation. The environment
   threshold remains an explicit owner choice; `90` is the reviewed
   recommendation, not an implicit default.
6. **Initial state:** `INSUFFICIENT_DATA` can be normal until CloudWatch has
   enough datapoints. Do not mutate alarm state merely to force a test.
7. **Delivery limitation:** without a subscriber or a natural state
   transition, connected verification proves alarm/action configuration and
   KMS authorization, not receipt by a human endpoint.
8. **Cost:** the change adds one standard metric alarm and no subscriber or
   workload. Any cost must still be accepted during the connected-plan review.

No accepted ADR changes. The remediation remains infrastructure foundation;
it creates no application runtime behavior and no agent/data access path.

## Offline implementation validation

Run without AWS credentials after implementation approval:

```text
python3 scripts/dev.py infra-preflight
python3 scripts/dev.py infra-format
python3 scripts/dev.py infra-validate
python3 scripts/dev.py infra-test
terraform -chdir=infrastructure/modules/observability test
terraform -chdir=infrastructure/modules/kms test
python3 scripts/dev.py infra-lint
python3 scripts/dev.py infra-security
python3 scripts/dev.py check
git diff --check
```

The offline stopping condition is all checks passing and a reviewed diff that
contains only the planned files and no credentials, generated state, backend
changes, subscription, extra alarm, or future-goal scope. Stop before any
connected Terraform command.

## Connected checkpoint sequence

Each numbered step requires separate explicit approval for account
`736956442295` and Region `ap-southeast-1`:

1. Add the owner-approved threshold to the ignored local development
   `terraform.tfvars`; run strict preflight.
2. Create a saved connected development plan only. Expected managed-resource
   actions are exactly one alarm create and one in-place observability KMS key
   policy update, with no replacement or destroy. Output-only changes are
   acceptable. Any other action is a hard stop for review.
3. Review plan JSON, Terraform version, account, Region, action counts, KMS
   policy conditions, alarm contract, and SHA-256. Do not apply during review.
4. Apply only the exact reviewed saved plan after separate hash-bound approval.
5. Perform read-only verification with `cloudwatch:DescribeAlarms` and KMS key
   metadata/policy inspection. Confirm the exact alarm name, metric, dimension,
   threshold, evaluation settings, action ARN, enabled actions, tags, and
   scoped KMS statement. Do not call `SetAlarmState` and do not publish to SNS.
6. Run a separately approved final `terraform plan -detailed-exitcode`; exit
   `0` is required.

No step authorizes `terraform destroy`, arbitrary AWS mutation, another smoke
task, a subscription, or a transition into Goal 4.

## Acceptance criteria

- Exactly one base RDS CPU alarm exists and is managed by Terraform.
- The alarm uses the managed RDS identifier, reviewed static metric contract,
  and owner-approved threshold.
- Its only action is the existing same-account encrypted alert topic.
- The KMS policy grants only the required CloudWatch publisher actions and is
  limited to the exact account and alarm ARN while retaining all existing key
  protections.
- No subscription or unrelated resource is introduced.
- Offline validation passes with contract coverage for positive and negative
  threshold cases and KMS-policy regression coverage.
- The reviewed connected plan contains only expected changes, the exact saved
  plan applies successfully, read-only alarm inspection passes, and the final
  detailed-exitcode plan returns `0`.
- Durable evidence is updated and committed before Goal 3A/3B is restored to
  `VERIFIED`.

## Review result and stopping condition

**Final review result: CONNECTED ACCEPTANCE PASS; DURABLE EVIDENCE COMMIT
PENDING.**

The plan closes the documented alarm gap with one resource and the minimum
supporting typed interface, encryption permission, tests, and runbook evidence.
It does not alter an ADR or expand into later goals.

The owner approved this plan for offline implementation and selected
`rds_cpu_alarm_threshold_percent = 90`. Core offline validation passed. The
ignored local development `terraform.tfvars` was deliberately not modified by
the source/tests/docs approval. Under a later local-input-only approval, the
owner-selected assignment was added and strict offline preflight passed on
`2026-08-08` with a structurally valid state KMS key ARN. `pip-audit` could not
run with network disabled because it queries PyPI; all other documented offline
checks completed.

Under separate connected-plan approval on `2026-08-08`, Terraform `1.10.5`
created a local saved development plan with SHA-256
`d3cfa2db71da41020eabe109913eba2fa97117176f0e7e13cfdc8a965c159712` for
account `736956442295` and Region `ap-southeast-1`. Offline JSON review found
exactly one `aws_cloudwatch_metric_alarm.rds_cpu_high` create and one in-place
`aws_kms_key.observability` policy update, with no replacement or destroy. The
threshold is `90`; the KMS update preserves the existing root and CloudWatch
Logs statements and adds only the exact-account, exact-alarm CloudWatch grant.
The plan was not applied and no task was run. When hash-bound apply approval
was later granted, the temporary artifact was no longer present, so no apply
command ran. Stop pending separate approval to create and review a new saved
plan; the expired approval was not reused for a different artifact.

Under that separate approval, a replacement saved plan was created on
`2026-08-08` at the Git-ignored workspace path
`infrastructure/environments/development/rds-cpu-alarm-remediation-20260808.tfplan`.
Its SHA-256 is
`db143549fe551a397afac6b88248b8be74b48b689fa8a685c6868af43816f331`.
Offline JSON review again confirmed exactly one alarm create and one in-place
observability KMS policy update, with no replacement, destroy, or other
managed-resource action. Under separate approval bound to that SHA-256, the
saved plan applied successfully as `1 added, 1 changed, 0 destroyed`.
Read-only CloudWatch inspection confirmed the complete alarm contract and its
only SNS action; read-only KMS inspection confirmed the exact new statement
and preservation of the root and CloudWatch Logs statements. No task,
alarm-state mutation, notification publish, replacement, or destroy occurred.
Under separate approval, the final connected development plan exited `0` with
`No changes`. Its Git-ignored saved artifact has SHA-256
`db9ec9f069bf03d724689d1cf2a3347a43dd63c18df81f99463f18bf649d78be`.
Offline JSON review confirmed zero non-no-op resource changes and zero
non-no-op output changes for the approved account, Region, and threshold.
Connected remediation acceptance therefore passes. Repository-level
`VERIFIED` status remains pending review and commit of the current durable
source, tests, documentation, and verification evidence.

The final offline blocker review on `2026-08-10` corrected the stale
chronological status text, replaced the unreliable post-stop EC2 ENI lookup in
the runtime-smoke wrapper with deterministic `assignPublicIp=DISABLED` plus
durable ECS private-attachment validation, and added a regression test. The
connected exact security-group and AOSS policy inspection is accepted as the
unauthorized-path rejection proof; no additional AWS task was run. All final
offline gates passed, including dependency audit. The only remaining gate is
durable commit provenance.
