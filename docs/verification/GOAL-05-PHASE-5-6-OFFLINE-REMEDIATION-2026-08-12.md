# Goal 5 Phase 5-6 offline remediation for strict bundle warning

Date: 2026-08-12  
Scope: offline-only correction after the one approved strict validation
reported an unmatched `sync.exclude` warning.

## Remediation

The explicit safety boundary remains unchanged:

```yaml
sync:
  exclude:
    - sql/goal_04/remediation/**
```

The remediation directory now contains only:

```text
databricks/sql/goal_04/remediation/README.md
```

The marker is non-executable documentation. It states that the directory must
not contain executable SQL and that future remediation requires separate review
and approval. No destructive or executable SQL was added.

The offline contract now requires the marker to exist with its reviewed content,
while continuing to fail closed if any `.sql` file appears under the directory.
A regression test covers a missing marker. README, runbook, and durable status
documentation now describe the marker and exclusion boundary.

## Offline evidence

| Check | Result |
| --- | --- |
| Goal 4 static validator | PASS |
| Goal 5 static validator | PASS |
| Ruff format check | PASS — 96 files formatted |
| Ruff lint | PASS |
| mypy strict | PASS — 13 source files |
| pytest | PASS — 119 tests |
| Coverage | PASS — 97.15% combined |
| Bandit | PASS |
| detect-secrets baseline hook | PASS |
| `git diff --check` | PASS |

The first pytest invocation used the wrong module-entry `sys.argv` shape and
produced two harness-only failures; the repository-standard sanitized argv
invocation then passed all 119 tests. No source behavior failure was observed.

The full bundle source aggregate remains
`eb4c7e6db55d9ec5aedf63480ecf00bb5cd404b9b64ddc1f4930d87ab1060368`, because
the marker is under the excluded remediation path and is not part of the
reviewed synchronized source set.

## Boundary

No connected bundle validation retry, deployment, SQL/job run, table/data
mutation, compute creation, Terraform operation, or AWS operation occurred in
this remediation. Goal 5 remains unverified.

The next separate approval is for exactly one strict connected
`databricks bundle validate` against target `development`, profile
`ask-david-development`, aggregate source SHA-256
`eb4c7e6db55d9ec5aedf63480ecf00bb5cd404b9b64ddc1f4930d87ab1060368`. It must
stop on any warning or error and must not deploy or execute jobs/SQL.
