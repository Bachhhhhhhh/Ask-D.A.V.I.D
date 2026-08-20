# Goal 6 Doris listener diagnosis and host-prerequisite remediation — offline evidence

Date: 2026-08-14
Environment: development only (`736956442295`, `ap-southeast-1`)
Scope: source, tests, runbook, and offline validation only

## Trigger and durable connected evidence

The approved readiness-marker apply completed with six reviewed replacements
and no other AWS action. Read-only EC2 inspection reported `ok/ok` for both
private instances, but the persisted bootstrap markers were:

```text
FE: {"goal":"goal-06","role":"fe","status":"doris-port-unavailable","port":"9030"}
BE: {"goal":"goal-06","role":"be","status":"doris-port-unavailable","port":"9050"}
```

No task was retried or launched after this failure. Existing security-group,
route/NACL, and VPC-flow evidence did not show a network drop. The evidence
therefore establishes a Doris process/listener blocker, but does not prove
whether startup exited or remained blocked inside the container.

## Diagnosis

The rendered bootstrap already supplies the official FE/BE discovery variables
(`FE_SERVERS`, `FE_ID`, and `BE_ADDR`) and private `priority_networks`. The
remaining repository gap was the host prerequisite contract documented by
Apache Doris: `vm.max_map_count=2000000` and a one-million-file-descriptor
limit. The prior bootstrap did not set either value and did not persist bounded
container diagnostics. This is the leading declarative hypothesis, not a claim
that the live host kernel value was directly observed; SSM was unavailable and
no ad-hoc shell was used.

Apache documents the relevant startup prerequisites in its [Doris Quick Start](https://doris.apache.org/docs/4.x/getting-started/quick-start/)
and the FE listener/configuration contract in its [FE configuration documentation](https://doris.apache.org/docs/4.x/admin-manual/config/fe-config/).

## Offline remediation implemented

- Terraform-owned `/etc/sysctl.d/99-goal6-doris.conf` and an immediate
  `vm.max_map_count=2000000` application with fail-closed status;
- PAM limits and a Docker systemd drop-in setting `LimitNOFILE=1000000`;
- explicit `--ulimit nofile=1000000:1000000` on the FE/BE container;
- `host-prerequisites-ready` / `host-prerequisites-failed` lifecycle markers;
- bounded, redacted `docker inspect` and `docker logs --tail 200` evidence in
  the encrypted role-volume `container-diagnostics.log`;
- no volume deletion, metadata reset, public ingress, IAM/KMS/network change,
  task launch, or retry.

## Offline validation

| Check | Result |
| --- | --- |
| Goal 6 static validator (`python3 scripts/validate_goal6.py`) | PASS |
| Goal 6 static regression tests (manual invocation of all 17 test functions) | PASS |
| Rendered FE/BE bootstrap `bash -n` | PASS |
| Python compile of changed validator/tests | PASS |
| `git diff --check` | PASS |
| Terraform `fmt -check` on tracked `.tf`/`.tftest.hcl` source | PASS — Terraform v1.15.8 restored from the local `/tmp` tool cache |
| Terraform `init -backend=false` with a local provider mirror | PASS |
| Terraform `validate` | PASS — provider schema loaded from the local mirror in the offline runtime |
| Terraform mock-provider tests | PASS — 7 passed, 0 failed |
| pytest/coverage, Ruff, mypy, Bandit, detect-secrets, TFLint, Trivy | UNVERIFIED — tools are not installed in this host |

No connected Terraform plan/apply/destroy, AWS/Databricks operation, ECR push,
ECS task, SQL/job run, or bundle operation occurred for this remediation.

## Next approval boundary

After offline validation passes, create one new saved connected development
Terraform plan. Review it for the exact expected FE/BE user-data replacement
set and zero unexpected IAM/KMS/network/S3/ECR/Databricks/public/
production/destroy actions. Do not launch a verifier task until both hosts
emit `doris-port-ready`.

## Connected follow-up result

That saved plan was subsequently applied with explicit hash-bound approval as
`6 added, 0 changed, 6 destroyed`. The replacement hosts reached
`host-prerequisites-ready`, but both still failed the listener guard with
`doris-port-unavailable` on ports `9030` and `9050`; cloud-init
`scripts-user` failed and no host log stream appeared. The durable apply
evidence is
`docs/verification/GOAL-06-DORIS-LISTENER-HOST-PREREQ-APPLY-2026-08-14.md`.
This confirms the host prerequisite remediation was applied but did not yet
prove Doris application readiness. No task was launched or retried.

## Updated diagnosis after the host-prerequisite apply

The host prerequisites reached `ready` on both replacement hosts, and both
images pulled successfully, so the remaining failure is inside Doris startup
or its persisted cluster state rather than the prerequisite guard. The same
Terraform apply reattached the existing FE metadata and BE serving-data
volumes to new private IPs (`10.42.69.177` and `10.42.77.49`) after the prior
hosts had used `10.42.64.238` and `10.42.71.97`. A read-only ENI inspection
found the prior addresses currently unassigned. This makes persisted
single-node cluster identity/IP state the leading hypothesis, but it is not
proven because SSM is unavailable and the host log stream was never created.

The current design is IP-based rather than Doris FQDN mode. Apache's [Doris
FQDN guidance](https://doris.apache.org/docs/4.x/admin-manual/cluster-management/fqdn/)
documents different server-IP-change behavior for FQDN-enabled clusters;
therefore a future declarative remediation should either preserve stable
private IPs for these persisted volumes or receive a separately approved
metadata migration/rebuild design. It must not delete the FE metadata or BE
serving-data volumes implicitly.

The approved next offline remediation is to add explicit Terraform-managed,
validated private-IP inputs (using the now-free prior addresses) and improve
failure evidence delivery. This source-only remediation now adds
`10.42.64.238` for FE and `10.42.71.97` for BE, validates that the inputs are
distinct and inside the selected subnet with Terraform's `cidrcontains`, and
fails closed if a host observes a different local address. No IP assignment,
volume reset, connected plan, or AWS mutation is performed by the offline
change.

Read-only subnet evidence supports the proposal: `subnet-09bc95f43115dca3e`
is `10.42.64.0/20` in `ap-southeast-1a`, reports `4088` available addresses,
and both prior addresses are inside that CIDR and currently unassigned. This
is feasibility evidence only; it is not an authorization to assign them.

The implementation and offline acceptance evidence for this approved
remediation are recorded in
`docs/verification/GOAL-06-DORIS-STABLE-PRIVATE-IP-OFFLINE-2026-08-14.md`.
