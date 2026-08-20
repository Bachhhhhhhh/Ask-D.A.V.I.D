# Goal 6 Phase 6-6 private verification-path closure

Date: 2026-08-17
Environment: development only (`736956442295`, `ap-southeast-1`)
Status: **PASS — PRIVATE DORIS FE PATH**

## Scope

This report closes only Phase 6-6: proving the approved private verifier can
reach the intended Doris FE query endpoint without public exposure or Codex-host
network access. It does not claim Unity Catalog/Iceberg interoperability,
serving-table refresh, or a successful future Query Service identity query.

## Positive reachability evidence

The separately approved one-off Fargate task
`f90b1e0ac7c342bfa4fcb4473f33c7cb` used task definition
`ask-david-development-doris-verifier:7` and stopped with exit code `0`.

| Control | Evidence | Result |
| --- | --- | --- |
| Private execution | ECS ENI `eni-0235da75a9ade9b4b`, private IP `10.42.39.89`, approved application subnet `subnet-0a1aad220d82ef879` | PASS |
| No public task address | `assignPublicIp=DISABLED`; subnet `MapPublicIpOnLaunch=false`; task attachment has no public association | PASS |
| Intended endpoint | Task-definition `DORIS_FE_HOST=10.42.64.238`; FE is private, running, and EC2 `ok/ok` | PASS |
| Query-port reachability | Bounded TLS `mysqladmin ping` received a MariaDB authentication-denied response from `10.42.64.238:9030` and exited `0` | PASS |
| Sandbox isolation | The only data-plane connection originated from the Fargate ENI; the Codex host used AWS control-plane APIs only | PASS |
| Ephemeral lifecycle | ECS task is `STOPPED`; its ENI is deleted | PASS |

The private endpoint is deliberately a Terraform-managed static FE address,
not a separately provisioned DNS name. Therefore DNS resolution is **N/A** for
this endpoint design; the required endpoint-reachability check is proven by the
successful direct private-IP connection above.

## Deterministic unauthorized-path evidence

Read-only EC2 security-group inspection proves the relevant Doris path is
least-privilege and SG-referenced only:

| Source / destination | Allowed Doris traffic | Evidence |
| --- | --- | --- |
| Verifier SG `sg-04eb1ebf613ceeadc` → FE SG `sg-019b900ee5601c208` | TCP `9030` only | Verifier egress references only FE SG for port `9030`; no CIDR on that rule |
| FE SG inbound `9030` | Verifier, admin, and BE SGs only | Three named SG references; no IPv4/IPv6 CIDR or prefix list |
| FE SG other inbound | `8030` admin-SG only; `9010` BE-SG only | No verifier broad access and no public Doris/admin ingress |
| FE / BE instances | no public IPv4 | Read-only EC2 inspection of FE `i-0d7b971ba56dc2395` and BE `i-0dd28df1b1b2c7923` |

The verifier and host SGs retain TCP/443 egress for required private AWS and
Databricks endpoint access via the existing private-subnet NAT/endpoint design.
That egress does not create a Doris listener path: the FE SG has no TCP/443
ingress and no database/admin CIDR ingress. No public IP, Internet Gateway
route, or CIDR rule is used for the verified FE TCP/9030 data path.

This is deterministic policy evidence that an unrelated SG has neither the
verifier's TCP/9030 egress grant nor the FE's TCP/9030 ingress grant. It is not
treated as proof of later SQL authorization, which is verified separately with
the dedicated query identity.

## Phase 6-6 result

| Requirement | Result |
| --- | --- |
| Approved private verifier environment | PASS |
| Intended private network and no public task IP | PASS |
| Doris endpoint resolves/reaches | PASS — direct static private endpoint; DNS N/A |
| Intended query port reachable | PASS |
| Unrelated direct Doris path rejected by policy | PASS — deterministic SG policy proof |
| No direct Codex-host connection required | PASS |
| Minimal health command | PASS — one bounded, non-query task; no retry |

Phase 6-6 is complete. The next phase remains separately approval-gated:
the private admin refresh will test governed Unity Catalog Iceberg REST access
and populate only disposable internal Doris serving objects.
