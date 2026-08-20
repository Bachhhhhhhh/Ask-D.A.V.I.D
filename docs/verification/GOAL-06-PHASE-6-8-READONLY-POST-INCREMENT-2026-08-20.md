# Goal 6 Phase 6-8 read-only verifier after controlled refresh

Date: `2026-08-20`

Status: `PASS — READ-ONLY RESULT CONTRACT`

## Approved contract

Exactly one private no-retry verifier task ran after the Phase 6-9 controlled
increment and Phase 6-7 admin refresh. The task definition contract was
revalidated before launch; no DDL, DML, refresh, rebuild, Terraform, ECR,
Databricks, or AWS control-plane mutation was performed.

| Input | Value |
| --- | --- |
| AWS account / Region | `736956442295` / `ap-southeast-1` |
| Cluster | `ask-david-development-cluster` |
| Task definition | `ask-david-development-doris-verifier:16` |
| Image | `sha256:a92d645deb0e67c88dc10a18d1bc796acc634ad5f3a9a666fcde7ca225ffc61e` |
| Private subnet / SG | `subnet-034f5f1c9bca753f1` / `sg-04eb1ebf613ceeadc` |
| FE target | `10.42.64.238:9030` |
| Public IP | `DISABLED` |

## Connected result

| Check | Result |
| --- | --- |
| Task | `9e399737d999478d9f8713d13b2485be` |
| Container | `doris-verifier`, exit code `0` |
| ENI / private address | `eni-0e33d687f62712a22` / `10.42.16.135` |
| CloudWatch stream | `verifier/doris-verifier/9e399737d999478d9f8713d13b2485be` |
| Operation marker | `readonly-verify / completed` |
| Source dataset | `ask_david_development.green_sm_business.goal5_structured_business_metrics` |
| Representative result | `2026-02-01`, `alpha`, event count `1`, metric total `10.5` |
| Serving row count | `3` |
| Source transformed at | `2026-08-13T04:24:56Z` |
| Serving refreshed at | `2026-08-20T06:11:29Z` |
| Executed query ID | `6266b477c74242d4-806213998d70f5cb` |
| Execution duration | `0` |

The CloudWatch stream also contains only known MariaDB program-name/TLS
warnings and no secret or credential values. The task exited successfully and
no retry was performed.

## Acceptance conclusion

Phase 6-8 read-only result-contract acceptance is **PASS**. The evidence
proves the private verifier can query the rebuilt serving copy, report source
provenance and refresh time, and return the required result-contract fields.
It does not by itself prove RBAC denial probes, query-limit enforcement,
increment idempotency, rebuild execution, or final zero drift.

## Boundary

Phase 6-10 disposable serving-copy rebuild and Phase 6-14 zero-drift/cleanup
remain outstanding. No additional task is authorized by this report.
