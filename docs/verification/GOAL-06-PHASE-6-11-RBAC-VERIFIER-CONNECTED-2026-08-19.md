# Goal 6 Phase 6-11 RBAC verifier — 2026-08-19

## Scope

One separately approved private RBAC verifier task ran from the Terraform-
created revision-14 verifier definition. It performed the positive serving
SELECT and the bounded negative authorization probes, then stopped. No retry,
Terraform, ECR, Databricks, source-table mutation, or unrelated AWS operation
occurred.

## Placement and task result

| Check | Result |
| --- | --- |
| AWS account / region | PASS — `736956442295` / `ap-southeast-1` |
| Cluster / task definition | PASS — `ask-david-development-cluster`, verifier `:14` |
| Image | PASS — `sha256:7e553ac62d231148d8384d1eeba44d2d8b639e357c34634fdc80bb2fde003d88` |
| Network | PASS — private subnet `subnet-034f5f1c9bca753f1`, no public IP |
| Security group | PASS — `sg-04eb1ebf613ceeadc` |
| Task ARN | `arn:aws:ecs:ap-southeast-1:736956442295:task/ask-david-development-cluster/1ba950f5ab7f47e490a36bb7afd17022` |
| Private IPv4 / ENI | `10.42.28.254` / `eni-0d5f2baadbf49eb38` |
| Exit status | PASS — `STOPPED`, exit code `0` |
| Running tasks after completion | PASS — `[]` |

## Authorization evidence

The sanitized completion evidence reports a positive SELECT with row count `2`
and explicit authorization denial evidence for every required negative class:

| Statement class | Result |
| --- | --- |
| INSERT | DENIED — authorization text |
| UPDATE | DENIED — authorization text |
| DELETE | DENIED — authorization text |
| CREATE | DENIED — authorization text |
| ALTER | DENIED — authorization text |
| DROP | DENIED — authorization text |
| Unauthorized database | DENIED — Doris privilege token |

The non-empty DELETE guard also passed: lower sentinel present, upper sentinel
present, and target key `127` absent. The DELETE probe therefore reached the
authorization check without mutating a row. No probe was reported as allowed.

## Current checkpoint

Phase 6-11 read-only identity validation is PASS. The next remaining connected
evidence is the controlled Phase 6-9 increment/refresh path, followed by the
disposable serving-copy rebuild, query-limit, audit, and final drift/cleanup
checks. Each mutation or task run requires its own approval boundary.
