# Goal 6 Doris log-signal classification — offline remediation

Date: 2026-08-14
Environment: development only (`736956442295`, `ap-southeast-1`)
Scope: source, tests, and documentation only

## Trigger

The exact approved diagnostics plan was applied successfully, but FE and BE
both remained running without binding ports 9030/9050. The safe summary showed
`error_present=false` and no host CloudWatch streams were available. Raw
container logs therefore could not be used to distinguish a listener bind,
configuration, metadata, or generic startup problem.

## Offline remediation

The Terraform-owned bootstrap now classifies the redacted tail of Docker logs
without emitting any log content. The status record adds only one bounded
value:

`log_signal = bind | metadata | configuration | exception | other | none`

Classification is fail-closed and diagnostic-only. It does not change Docker
arguments, ports, persisted volumes, IAM/KMS, network exposure, or retry
behavior. No raw log or credential can enter console output through this
classification path.

## Offline validation

| Check | Result |
| --- | --- |
| `python3 scripts/validate_goal6.py` | PASS |
| Goal 6 static/regression tests | PASS — 18 passed |
| Render-equivalent FE/BE bootstrap `bash -n` | PASS |
| Python compilation | PASS |
| `git diff --check` | PASS |

Terraform connected plan/apply, AWS/Databricks mutation, ECS task, SQL/job,
bundle operation, ECR operation, volume reset, and metadata deletion were not
performed for this follow-up.

## Next approval boundary

Create a new saved connected development Terraform plan only after review. It
must contain the FE/BE bootstrap replacements required for this classification
and no other action. Apply requires a new exact-plan approval. The next
read-only inspection will use `log_signal` to choose a declarative runtime or
persisted-state remediation; it must not infer that a volume is irrecoverable
or reset one implicitly.
