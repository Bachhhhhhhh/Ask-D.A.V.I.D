# Goal 6 RBAC DELETE probe remediation — offline

Date: `2026-08-19`

Status: **OFFLINE VALIDATED — SUBSEQUENT LOCAL IMAGE BUILT/SCANNED; NOT PUSHED, DEPLOYED, OR EXECUTED**

## Trigger and root cause

The approved revision-10 RBAC retry proved principal-specific authorization
denials for INSERT and UPDATE, but the DELETE probe returned success. The exact
statement was:

```sql
DELETE FROM ask_david_serving_development.goal6_authorization_probe WHERE FALSE
```

Version-bound Apache Doris 4.0.1 source confirms that the constant-false plan
becomes a `PhysicalEmptyRelation`; `DeleteFromCommand` processes that empty
relation and returns before its later `LOAD_PRIV` check. The statement changed
no data, but its success cannot prove DELETE authorization boundaries.

## Minimal remediation

Only `docker/doris-verifier/doris-rbac-verify` executable behavior changed:

1. bind reserved valid `TINYINT` key `127`;
2. use the query-only identity to require an exact zero count for that key in
   the disposable `goal6_authorization_probe`;
3. stop before DELETE with a sanitized fail-closed marker if the query fails or
   the key exists;
4. attempt `DELETE ... WHERE probe_id = 127`, which cannot take the
   constant-false empty-plan shortcut; and
5. accept only the existing explicit authorization classifications, retaining
   `unexpected-allow` as failure.

The precondition proves there is no target row, so even an unexpectedly allowed
DELETE affects zero rows. The probe never targets serving results, Unity
Catalog, S3, or authoritative data. INSERT, UPDATE, DDL, and unauthorized-
database probe statements are unchanged.

The reproducible image-input aggregate covers
`docker/Dockerfile.doris-verifier`, every regular file under
`docker/doris-verifier/`, and every regular file under `doris/`, using the
established sorted per-file SHA-256 manifest method:

```text
c468b8fde5b00aacb208d460099b408b9893912a845a5d48b8f1b59b6647dc64
```

## Offline evidence

| Check | Result |
| --- | --- |
| POSIX shell parse | PASS — `sh -n docker/doris-verifier/doris-rbac-verify` |
| Static contract validator | PASS — `python3 scripts/validate_goal6.py` |
| Goal 6 regression suite | PASS — 43 tests |
| Goal 5 + Goal 6 cross-goal regression suite | PASS — 50 tests |
| Python source compilation | PASS |
| Terraform formatting/validation/tests | NOT RUN — installed Terraform is Snap-packaged and `snap-confine` lacks `cap_dac_override` in this sandbox; no Terraform source changed |
| TFLint / Trivy configuration checks | NOT RUN — executables are absent; no Terraform or image source outside this runner changed |
| Repository Ruff/mypy/Bandit/audit/secret-hook orchestration | NOT RUN — `uv` and those executables are absent; the Pydantic-dependent Goal 2 suite is outside Goal 6 acceptance |
| Diff integrity | PASS — tracked diff check plus explicit trailing-whitespace scan of the Goal 6 files |

Regression coverage proves that the runner:

- never restores DELETE `WHERE FALSE`;
- requires the reserved-key count before DELETE;
- stops without issuing DELETE when that count is non-zero;
- orders the absent-key precondition before DELETE;
- fails closed if DELETE unexpectedly succeeds; and
- continues accepting only explicit authorization text or canonical Doris
  privilege-token evidence.

The two `.pytest_cache` permission warnings are non-test cache-write warnings;
all selected tests passed. The tooling marked NOT RUN is reported explicitly
and is not inferred from historical runs.

## Connected boundary

The source-remediation operation did not build or push an image, change
Terraform or an ECS task definition, run an ECS task, execute Doris SQL, or
call AWS/Databricks. A subsequent, separately approved local-only checkpoint
built and scanned the exact aggregate above. Its evidence is
`docs/verification/GOAL-06-RBAC-DELETE-PROBE-IMAGE-BUILD-SCAN-2026-08-19.md`.
The deployed revision-10 digest remains unchanged and does not contain this
source correction.

Next, promotion of the exact scanned local artifact to an immutable ECR tag,
the Terraform-managed task-definition revision, and exactly one private
no-retry RBAC run each require separate approvals. Phase 6-11 remains partially
verified until all denial classes complete successfully in connected evidence.
