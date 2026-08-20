# Goal 6 Doris private cluster egress remediation — offline evidence

Date: 2026-08-17

Environment: development source only (`736956442295`, `ap-southeast-1`)

Status: offline implementation and validation only. No connected Terraform
plan/apply/destroy, AWS/Databricks mutation, instance replacement, ECS task,
SQL operation, or volume operation was performed for this remediation.

## Trigger and deterministic cause

The current checkpoint has no independently reconstructable live
`doris-port-ready` evidence for the current FE and BE hosts. Repository source
and the previously applied serving-state rebuild plan provide a deterministic
network-contract finding:

- FE and BE each had only TCP `443` egress;
- BE ingress allowed FE on `9050`, `9060`, and `8060`;
- FE ingress allowed BE on `9010`;
- no BE-initiated path to FE query port `9030` existed;
- no FE egress matched the three approved FE-to-BE membership ports.

The official Apache Doris BE Docker bootstrap connects to FE `9030` to inspect
membership and execute backend registration. FE initiates heartbeat/RPC
traffic to the BE membership ports. Security groups are stateful for response
traffic, but the initiating direction still needs an outbound rule and the
destination needs a matching inbound rule. The prior ingress-only model could
not satisfy that contract.

The branch-4.0 BE image source makes the observed state deterministic rather
than speculative: `init_be.sh` fixes its MySQL port at `9030`, executes
`SHOW FRONTENDS`, `SHOW BACKENDS`, and `ALTER SYSTEM ADD BACKEND` against the
FE, and only then invokes `start_be.sh --console`. Consequently, the Docker
container can remain `running` while the BE process and listener `9050` do not
yet exist when the FE control connection is blocked. The earlier
`log_signal=configuration` value was only a broad redacted-log classifier; it
is not used as proof of the root cause.

Primary behavior references:

- [Apache Doris 5-minute quick start](https://doris.apache.org/docs/dev/getting-started/quick-start/)
  documents FE query port `9030`, BE heartbeat port `9050`, and BE
  registration through `ALTER SYSTEM ADD BACKEND`;
- [Apache Doris ADD BACKEND](https://doris.apache.org/docs/4.x/sql-manual/sql-statements/cluster-management/instance-management/ADD-BACKEND/)
  defines the backend host/heartbeat registration contract;
- [Apache Doris branch-4.0 BE image bootstrap](https://github.com/apache/doris/blob/branch-4.0/docker/runtime/be/resource/init_be.sh)
  establishes the FE `9030` registration-before-BE-start execution order.

The filtered offline plan inspection used
`goal-06-doris-serving-state-rebuild-20260814.tfplan` and showed exactly the
two HTTPS egress rules plus the existing ingress rules; it did not expose or
print sensitive plan values.

## Remediation

Terraform now declares five development-only, SG-to-SG rules:

1. BE egress to FE TCP `9030`;
2. FE ingress from BE TCP `9030`;
3. FE egress to BE TCP `9050`;
4. FE egress to BE TCP `9060`;
5. FE egress to BE TCP `8060`.

No rule uses a CIDR and no public ingress is introduced. Existing narrow
HTTPS egress remains unchanged.

BE bootstrap now also waits for the private FE `9030` registration path before
launching the BE container. The probe is TCP-only, credential-free, and
bounded. It records `fe-registration-port-waiting`, then either
`fe-registration-port-ready` or the terminal
`fe-registration-port-unavailable` marker. This removes the concurrent
first-boot race without retrying SQL, broadening access, or changing a volume.

The ignored development `terraform.tfvars` now explicitly keeps
`goal_6_rebuild_serving_state = true`. This retains the fresh encrypted FE/BE
rebuild volumes as desired state and prevents the next plan from attempting to
select the old detached volumes. The ignored file is not a commit candidate.

The previously implemented early bootstrap markers remain required. A future
approved apply must produce fresh, instance-specific `bootstrap-invoked`,
ready diagnostics summaries, and `doris-port-ready` markers for FE `9030` and
BE `9050`. An EC2 running/healthy state or container ID alone is insufficient.

## Offline validation

Commands:

```text
python3 scripts/validate_goal6.py
python3 -m pytest -o addopts='' -q tests/unit/test_goal6_static.py tests/unit/test_goal5_static_goal6_regression.py
terraform fmt -check -recursive infrastructure
bash -n infrastructure/modules/doris-serving/templates/doris-host.sh.tftpl
terraform validate
terraform test -test-directory=tests
git diff --check
```

Observed results:

- Goal 6 static validator: PASS;
- targeted Goal 6/Goal 5 regression tests: PASS (`20 passed`); pytest emitted
  two non-test-failing cache warnings because the existing `.pytest_cache` is
  not writable;
- Terraform recursive formatting check: PASS;
- development-root Terraform validation: PASS;
- development-root Terraform mock tests: PASS (`7 passed`, `0 failed`);
- isolated `doris-serving` module validation: PASS using a backend-disabled
  `/tmp` copy and the existing local provider cache;
- isolated module regression test for the five private rules: PASS (`1
  passed`, `0 failed`);
- rendered-template shell syntax and targeted Python compilation: PASS;
- `git diff --check`: PASS.

`make goal6-static` was not run because `uv` is not installed. Its underlying
Goal 6 validator and the targeted pytest suite were executed directly. TFLint,
Trivy, Ruff, mypy, Bandit, and detect-secrets executables are not installed in
this environment and were not run. No Pydantic-dependent check is a Goal 6
acceptance requirement.

## Next approval boundary

Create one saved connected development plan only after AWS identity can be
reverified. The plan must be reviewed with these fail-closed conditions:

- Terraform-managed serving-data `aws_ebs_volume`
  create/update/replace/destroy: zero (replacement EC2 root block devices are
  reviewed as part of the host replacements, not as dedicated data volumes);
- old detached volume reattachment: zero;
- public exposure and production actions: zero;
- unrelated AWS/Databricks actions: zero;
- only the five reviewed SG rule creates and the minimum host/user-data
  replacement/attachment actions required to deliver the bootstrap evidence
  are acceptable.

Applying that exact saved plan requires a separate hash-bound approval. After
apply, read-only console/CloudWatch inspection must prove both current instance
IDs emitted `doris-port-ready`; otherwise stop without an ECS task retry.
