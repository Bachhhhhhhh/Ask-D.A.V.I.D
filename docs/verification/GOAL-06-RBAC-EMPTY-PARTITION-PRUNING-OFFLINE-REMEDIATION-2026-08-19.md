# Goal 6 RBAC empty-partition pruning remediation — offline

Date: `2026-08-19`

Status: **OFFLINE VALIDATED — SUBSEQUENT LOCAL IMAGE BUILT/SCANNED; NOT PUSHED OR DEPLOYED**

## Scope

The revision-11 RBAC task proved INSERT and UPDATE authorization denials but
showed that a reserved-key DELETE against an entirely empty disposable table
was still pruned before Doris 4.0.1 reached its `LOAD_PRIV` check.

The minimal source correction changes only the DELETE evidence path:

1. retain the query-only reserved-key `127` absence precondition;
2. execute `SET disable_empty_partition_prune = true` and the reserved-key
   DELETE in one MariaDB client session;
3. retain the existing authorization-only rejection classifier; and
4. fail closed on precondition failure, wrong rejection layer, or an allowed
   DELETE.

The same-session setting prevents the empty-partition rewrite from short-
circuiting the privilege check. The independently established absent-key
precondition guarantees zero matching rows even if permissions were
unexpectedly broadened. No serving-result, Unity Catalog, S3, or authoritative
object is used as a negative-test target.

## Offline evidence

Validation results are recorded after executing the repository checks:

| Check | Result |
| --- | --- |
| POSIX shell parse | PASS — `sh -n docker/doris-verifier/doris-rbac-verify` |
| Goal 6 static validator | PASS — `python3 scripts/validate_goal6.py` |
| Goal 6 regression tests | PASS — 43 tests |
| Goal 5 + Goal 6 cross-goal tests | PASS — 50 tests |
| Python compilation | PASS |
| Diff integrity | PASS for the remediation diff — `git diff --check` and explicit scan of the touched source/report files |

Regression scope requires the setting and DELETE to occur in the same command,
requires the precondition to precede that command, rejects reintroduction of
`WHERE FALSE`, and retains the fail-closed unexpected-allow path.

The repository's default pytest options require the absent `pytest-cov`
plugin, so the first pytest invocation stopped during argument parsing before
collection. The focused suites were rerun with `-o addopts=''`; this disables
only repository coverage arguments and produced the passing counts above. Two
warnings report that pre-existing `.pytest_cache` permissions prevent cache
writes; they do not represent test failures.

The explicit wider scan also found trailing spaces on lines 3–4 of the
pre-existing, untracked Goal 6 plan header. Those lines were outside this
remediation and were not changed; no remediation-touched line has trailing
whitespace.

The reproducible sorted per-file image-input aggregate for
`docker/Dockerfile.doris-verifier`, `docker/doris-verifier/**`, and `doris/**`
is:

```text
3195354def2b35b9d2ca828594ae455e593906689a46145e2ba7b05bcf19a7f5
```

The remediated runner SHA-256 is:

```text
1cfd355469a54a7014a97bbf27b6c084b1d2180fecf11b386f6d8e379cda9ec7
```

## Connected boundary

This remediation itself did not build or push an image, change Terraform or an
ECS task definition, run an ECS task, execute connected Doris SQL, or call AWS
or Databricks. A subsequent, separately approved checkpoint built and scanned
the exact source aggregate above; its evidence is
`docs/verification/GOAL-06-RBAC-EMPTY-PARTITION-PRUNING-IMAGE-BUILD-SCAN-2026-08-19.md`.
No ECR push or deployment has occurred. Phase 6-11 remains only partially
verified.
