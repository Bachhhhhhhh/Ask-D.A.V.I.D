# Goal 6 SMALLINT probe remediation image ECR promotion — 2026-08-19

## Scope

The separately approved promotion pushed the already built and locally scanned
Goal 6 verifier image to the private development ECR repository. No Terraform,
ECS task, Doris SQL, Databricks operation, or unrelated AWS resource mutation
was performed.

## Preconditions and identity

| Check | Result |
| --- | --- |
| AWS identity | PASS — account `736956442295`, principal `bach_dev_admin_david` |
| AWS region | PASS — `ap-southeast-1` |
| Repository | PASS — `ask-david-development/doris-verifier` |
| Tag availability before promotion | PASS — `goal6-smallint-probe-6fa3d0c9` was absent |
| Tag policy | PASS — repository tag mutability is `IMMUTABLE` |
| Registry scan configuration | PASS — scan-on-push is enabled |

## Promoted artifact

| Attribute | Value |
| --- | --- |
| Source aggregate | `6fa3d0c9b55e8fe22916c7448ea44d12de3f750ee047ff6b8cfed34f44458f78` |
| Local image tag | `ask-david-doris-verifier:goal6-smallint-probe-6fa3d0c9` |
| Immutable ECR tag | `736956442295.dkr.ecr.ap-southeast-1.amazonaws.com/ask-david-development/doris-verifier:goal6-smallint-probe-6fa3d0c9` |
| Local image digest | `sha256:7e553ac62d231148d8384d1eeba44d2d8b639e357c34634fdc80bb2fde003d88` |
| ECR digest after push | `sha256:7e553ac62d231148d8384d1eeba44d2d8b639e357c34634fdc80bb2fde003d88` |
| Digest match | PASS |
| ECR image size | `17,892,949` bytes |

Docker authenticated only for the push and logged out through an exit trap. No
credential value was displayed or added to this repository.

## Scan evidence

The approved local Trivy `0.70.0` scan of the exact digest found zero
HIGH/CRITICAL vulnerabilities; see
`GOAL-06-RBAC-NONEMPTY-DELETE-PROBE-SCHEMA-IMAGE-BUILD-SCAN-2026-08-19.md`.

The repository has scan-on-push enabled, but immediate read-only
`describe-image-scan-findings` returned `ScanNotFoundException`. Consequently,
ECR registry scan findings are **UNVERIFIED** at this checkpoint and are not
represented as a passing scan.

## Current checkpoint

The image is available under the immutable development tag above. The next
operation requires separate approval: update only ignored development tfvars,
run offline preflight, and create a saved connected Terraform plan restricted
to the two Goal 6 task-definition revisions that reference this exact digest.
