# Goal 6 MariaDB TLS option remediation — offline implementation

Date: 2026-08-13
Scope: runner source, static validation, regression tests, and documentation
Connected AWS/Databricks operation: none

## Root cause

The single approved post-remediation admin task used the deployed revision-2
image and stopped with exit code `7`. Redacted CloudWatch output was:

```text
mysql: unknown variable 'ssl-mode=REQUIRED'
```

The image installs Alpine `mariadb-client`; `--ssl-mode` is a MySQL-specific
option and is rejected by that client. The failure occurred before the Doris
admin-refresh operation, so no Doris/lakehouse result was established.

## Approved offline correction

MariaDB's official client documentation defines `--ssl` as the MariaDB option
that enables TLS. The three Goal 6 runners now use `--ssl --protocol=TCP` and
contain no `--ssl-mode` option:

- `docker/doris-verifier/doris-admin-refresh`;
- `docker/doris-verifier/doris-readonly-verify`;
- `docker/doris-verifier/doris-rebuild-serving`.

Certificate verification was not added in this remediation because the
development design uses the Doris built-in certificate and has no approved CA
file. Custom CA/mTLS remains a separate security decision. The runners still
fail closed if the TLS connection cannot be established.

Static validation now requires the MariaDB option and rejects
`--ssl-mode`. A regression test covers all three runners. The Goal 6 plan now
documents the MariaDB-compatible TLS contract.

The 13-file verifier source set (sorted repository-relative paths; aggregate is
the SHA-256 of the newline-delimited per-file `sha256sum` output) currently
has fingerprint:

`ab6bc4dceabf86134ac526707b592d1e95137076ecbf55343b12eabfcee5b142`

## Offline validation

| Check | Result |
| --- | --- |
| `python3 scripts/validate_goal6.py` | PASS |
| `python3 -m py_compile scripts/validate_goal6.py tests/unit/test_goal6_static.py` | PASS |
| `sh -n` on all three runner scripts | PASS |
| `git diff --check` | PASS |
| `pytest` | NOT RUN — executable unavailable on this host |
| Ruff | NOT RUN — executable unavailable on this host |
| Docker image build | NOT RUN — Docker daemon unavailable on this host |
| ECR push, Terraform, AWS, Databricks, ECS task | NOT RUN |

The deployed ECR image and ECS task definitions are unchanged. A new
immutable image build/scan/push and any task-definition update require separate
connected approvals before another task attempt.
