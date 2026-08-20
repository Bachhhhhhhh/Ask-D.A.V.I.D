# Goal 6 RBAC rejection-classifier remediation — offline

Date: `2026-08-18`

Status: `OFFLINE VALIDATED — LOCAL IMAGE BUILT, NOT PUSHED, DEPLOYED, OR EXECUTED`

## Triggering connected evidence

The one approved revision-9 RBAC verifier task,
`be576a484aa6438a82cbc3509a4b8a00`, exited `1` on its first `insert` probe and
emitted only this durable sanitized event:

```json
{"goal":"goal-06","operation":"rbac-verify","status":"wrong-rejection-layer","statement_class":"insert"}
```

The runner intentionally suppressed raw database stderr to avoid logging a
password or sensitive server detail. Consequently, the exact live wording is
not reconstructable and this report does not infer it. No retry occurred.

## Remediation

`docker/doris-verifier/doris-rbac-verify` now accepts a failed negative probe
only when its captured stderr contains either:

- an explicit authorization phrase (`access denied`, `permission denied`,
  `not authorized`, or a bounded `not allowed to execute/perform/access`);
- a canonical Doris privilege token matching `*_PRIV`, such as `LOAD_PRIV`.

All other failures, including syntax, parser, object, connection, and runtime
errors, continue to emit `wrong-rejection-layer` and fail. Successful mutation
probes remain `unexpected-allow` failures. The accepted event exports only the
non-sensitive classification `denial_evidence` (`authorization_text` or
`doris_privilege_token`); raw stderr is not exported.

Apache Doris documents canonical privilege names such as `LOAD_PRIV` as the
required authorization for data load operations. This validates the use of a
privilege-token discriminator without treating generic MySQL error codes as
authorization proof. [Apache Doris documentation](https://doris.apache.org/docs/4.x/data-operate/import/data-source/huawei-obs/)

## Offline validation

| Check | Result |
| --- | --- |
| POSIX shell syntax for `doris-rbac-verify` | PASS |
| Existing explicit authorization-text mock | PASS |
| New Doris `LOAD_PRIV` mock | PASS |
| New syntax-error fail-closed mock | PASS |
| Focused Goal 6 static regression suite | PASS — 40 tests |
| Goal 6 static validator | PASS |
| `git diff --check` | PASS |
| Local image build, non-root inspection, and network-disabled runner parse | PASS — source aggregate `25b0956680a6765fcb5e2f5034208da8e6d3e5b4817ccada3c07030af681bff5`; local OCI image ID `sha256:c7e9cbc1e0a330fe17397d5509f0ec4618a450b489b342128ef20c59040834c6`; Linux/amd64; UID/GID `65532:65532` |
| Trivy `0.69.3` HIGH/CRITICAL vulnerability scan with `--ignore-unfixed` | PASS — zero findings for Alpine `3.21.7` |

The exact commands were:

```text
bash -n docker/doris-verifier/doris-rbac-verify
python3 -m pytest -o addopts='' tests/unit/test_goal6_static.py -q
python3 scripts/validate_goal6.py
git diff --check
docker build --pull=false --tag ask-david-doris-verifier:goal6-rbac-25b09566 -f docker/Dockerfile.doris-verifier .
docker run --rm --network none ... sh -n <each fixed runner>
docker run --rm --network host ... trivy image ...  # download public vulnerability DB only
docker run --rm --network none ... trivy image --skip-db-update --offline-scan ...
```

The Docker bridge could not download the public Trivy DB. The approved fallback
used host networking only for that DB download; the actual local-image scan then
ran with networking disabled, a read-only Docker socket, and the local cache.

## Connected boundary

This change has not pushed an image, changed Terraform/ECS, or run a task. The
current revision-9 verifier image is unchanged. The required local image scan
now passes. A later immutable ECR push, Terraform task-definition revision,
and one no-retry RBAC task each require separate approval.

## Read-only ECR promotion preflight

The following read-only checks passed after the local scan:

| Check | Result |
| --- | --- |
| AWS account | PASS — `736956442295` (`bach_dev_admin_david`) |
| Region | PASS — `ap-southeast-1` |
| Repository | PASS — `ask-david-development/doris-verifier` |
| Tag policy | PASS — `IMMUTABLE` |
| Scan on push | PASS — enabled |
| Destination tag availability | PASS — `goal6-rbac-25b09566` returned `ImageNotFoundException`, so no immutable tag will be overwritten |

This inspection did not authenticate Docker to ECR, push an image, or mutate
any AWS resource. It only establishes the exact future promotion destination.
