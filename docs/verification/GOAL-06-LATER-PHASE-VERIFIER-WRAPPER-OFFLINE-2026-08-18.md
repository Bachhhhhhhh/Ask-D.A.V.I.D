# Goal 6 later-phase verifier wrapper — offline implementation

Date: `2026-08-18`

Status: `OFFLINE VALIDATED — NO TASK RUN`

## Purpose

The pushed later-phase image contains three non-destructive runners that use
only the future Query Service read-only secret. This checkpoint adds one
repository-owned Bash execution boundary for them:

```text
infrastructure/scripts/run-goal6-verifier.sh
```

The wrapper does not add a service or implement Goal 8. It is a one-off Goal 6
verification harness only.

## Allowlisted modes

| Wrapper operation | Fixed container command | Intended phase |
| --- | --- | --- |
| `readonly` | `/app/doris-readonly-verify` | 6-8/6-13 result contract |
| `rbac` | `/app/doris-rbac-verify` | 6-11 authorization |
| `query-limit` | `/app/doris-query-limit-verify` | 6-12 resource protection |

Rebuild and audit are deliberately excluded because they require the admin
task definition and separate privilege/destructive boundaries.

## Fail-closed controls

Before launching anything, the wrapper requires and validates:

- explicit `--confirm-goal6-verifier`;
- account `736956442295` supplied at invocation and exact live identity match;
- exact region `ap-southeast-1`;
- exactly two private application subnets;
- one verifier security group;
- digest-pinned image, exact active task-definition revision, and family;
- Fargate/`awsvpc`, CPU/memory, execution role, and verifier task role;
- one `doris-verifier` container with the fixed default read-only command;
- only `DORIS_FE_HOST` environment and only `DORIS_QUERY_SECRET` secret;
- the expected CloudWatch log group/region/prefix;
- `assignPublicIp=DISABLED`;
- a command override drawn only from the three hard-coded modes.

It launches exactly one task, never retries, requires exit code zero, verifies
the task's private subnet/address, reads only the one expected log stream, and
returns only parsed Goal 6 JSON evidence containing a completed marker. It
never prints raw log messages or retrieves a secret value.

## Offline validation

| Check | Result |
| --- | --- |
| Bash parse | PASS |
| Missing-confirmation fail-closed execution | PASS — exit 1 before AWS CLI invocation |
| Goal 6 static validator | PASS |
| Goal 6 plus Goal 5 regression tests | PASS — 36 tests |
| `git diff --check` | PASS |

Two pytest cache warnings remain non-failing because the existing repository
cache directory is not writable.

## Reviewed hashes

- wrapper: `b0c39523f520c0ae94527cce36d90b81a8d206fc2b774f0e5524210a7d358379`;
- static validator after the companion admin-operation wrapper was added:
  `4dc6b5f864790c00cd44ee19a5a622a603f6453f5ca84ee0e4bb2aea21840ee5`;
- static tests after the companion admin-operation wrapper was added:
  `9218e33d841a1f655c4277645e0e1ff5e1e218cb57e29fa4e758b394b93b99cd`.

The final combined focused suite contains 38 passing tests after the Phase 6-9
increment audit was added; the verifier
wrapper itself remains unchanged at the hash above.

The wrapper is outside the verifier-image source aggregate and therefore does
not change pushed image digest
`sha256:2c2e35c82a23b57255522ad4e1034c21c76a60bff0d351ae4754f0dbaaa9c510`.

## Boundary

No tfvars edit, Terraform operation, AWS/Databricks/Doris mutation, ECR push,
or ECS task occurred. The next step remains separate approval for the ignored
image input, offline preflight, and a saved plan limited to the two Goal 6 task
definitions. Every later wrapper invocation still requires its own exact task
approval.
