# Goal 4 authorization and direct-path verification

## Scope and approval boundaries

This report records two separately approved one-shot negative jobs, the
separately approved deterministic connected read-only Unity Catalog and AWS
policy inspection, and the approved offline evidence-contract remediation.

No negative job was retried. The policy inspection performed no Databricks or
AWS mutation. The offline remediation changes SQL comments, static validation,
regression tests, and documentation only. It does not authorize connected
bundle validation/deployment, another SQL/job run, Terraform plan/apply/destroy,
or an AWS/Databricks mutation.

## Protected-table principal-specific rejection

- Job ID: `187789722076444`.
- Job run ID: `231413013546726`.
- Task run ID: `210727807599395`.
- Task: `denied_table_query_must_fail`.
- Attempt: `0`.
- Run-as application ID:
  `e06d5a6f-84f7-4dee-89a9-028c8541db8b`.
- Databricks job result: `ERROR / RUN_EXECUTION_ERROR`.
- Acceptance error: `INSUFFICIENT_PERMISSIONS`.
- Detail: no `USE CATALOG` on `ask_david_development`.
- SQLSTATE: `42501`.

The expected-failure job is not a successful Databricks job. Its task output is
positive security evidence because the synchronized SQL file loaded, the query
reached Unity Catalog, and Unity Catalog rejected the exact denied principal.
This satisfies acceptance criterion 27.

The earlier run `401673129115320` remains non-evidence because it failed before
SQL execution when the denied principal could not load the workspace file.

## Managed-storage structural rejection

- Job ID: `992194321630936`.
- Job run ID: `791479735507837`.
- Task run ID: `263272690337919`.
- Task: `denied_path_query_must_fail`.
- Attempt: `0`.
- Run-as application ID:
  `e06d5a6f-84f7-4dee-89a9-028c8541db8b`.
- Databricks job result: `ERROR / RUN_EXECUTION_ERROR`.
- Path-control error:
  `INVALID_PARAMETER_VALUE.LOCATION_OVERLAP`.
- Enforcement point: `CheckPathAccess`.

`LOCATION_OVERLAP` is a structural Unity Catalog managed-storage guard. It is
not a principal-specific authorization decision and is not accepted alone as
proof that the denied principal lacks storage access. It counts only with the
clean live policy evidence below.

## Live Unity Catalog policy evidence

Read-only inspection verified:

- exactly one denied-test service principal with the approved application ID;
- only `workspace-access` and `databricks-sql-access` entitlements;
- no data-engineer, business-reader, or governance-admin membership;
- no effective privilege for the denied principal or its default account
  groups on the storage credential, catalog, six schemas, protected table, or
  seven external locations;
- storage credential owner `ask-david-development-governance-admins`, isolated
  mode, and the expected AWS IAM role;
- exactly seven project external locations, all isolated, using only the
  Terraform-managed credential and approved Goal 3 S3 prefixes;
- only the governance-admin group can create external locations or managed
  storage;
- data-engineers have the planned catalog/schema data privileges and business
  readers have only Business-layer read privileges; and
- storage credential, all seven external locations, and the catalog bind
  read-write only to development workspace `7474644358733471`.

## Live AWS policy evidence

Read-only inspection in account `736956442295`, Region `ap-southeast-1`,
verified:

- IAM role `ask-david-development-unity-catalog-storage` is Terraform tagged;
- trust contains exactly the credential-reported Unity Catalog master role and
  the role self-principal;
- the external-ID condition exists and matches the storage credential without
  recording or printing its value;
- exactly one inline policy exists and no managed policy is attached;
- bucket discovery is limited to the six approved buckets;
- list access is limited to the seven approved
  `unity-catalog/development/*` roots;
- object access is limited to those seven managed roots;
- KMS use is limited to the development storage key;
- the KMS key is enabled, customer-managed, and its policy contains only
  account-root delegation plus the storage role statement; and
- all six backing bucket policies contain exactly the TLS-only deny statement
  and no `Allow` principal.

The first read-only `GetKeyPolicy` call used an alias that this KMS API does not
accept. The corrected call used the discovered exact key ID and returned the
policy above. This parameter correction did not mutate AWS.

The Databricks service-principal application ID is not an AWS principal and
appears in no IAM, KMS, or S3 grant. The policy chain exposes storage only
through the Unity Catalog credential role.

## Acceptance conclusion

| Criterion | Result | Evidence |
| --- | --- | --- |
| 27. Unauthorized table access is rejected | PASS | Principal-specific `INSUFFICIENT_PERMISSIONS`, SQLSTATE `42501` |
| 28. No direct S3 governance bypass exists | PASS | Managed-path `LOCATION_OVERLAP` plus clean live UC/IAM/KMS/S3 inspection |

The conclusion does not relabel `LOCATION_OVERLAP` as a permission error. It
uses the path guard as structural evidence and the policy inspection as the
principal-specific storage-isolation evidence.

## Comment-only source contract

The remediation documents the two distinct acceptance contracts without
changing executable SQL:

| SQL file | Full source SHA-256 after remediation | Executable-only SHA-256 before and after |
| --- | --- | --- |
| `11_denied_table_access.sql` | `f4872f7af8d0bbacc3c7813f604f55c3e3f13e79a6a9c969e75d0fcbcad022d9` | `739b582c05dc7c7797dac11b737bb989ff2a5451ae48ae9dd02096c3b6750337` |
| `12_denied_direct_path_access.sql` | `486e0e6cce822f470f540ff89907def96f1f817162ab95d529014403cb8218c9` | `a02c465782a4a5038b1b76a1d625211bdc8829ae12720ea97c5a661072c259ac` |

Reviewed aggregate bundle-source SHA-256 after remediation:
`fb31ecadd9add4b4f5984812a17b4ae3a88344b836e7b4d547a3058c0874e437`.

`databricks.yml` remains
`4f8f038137ba72bc955493b77fa08ec1bbb9469a04b02228b4bdb8f286d176b5`.
The resource manifest remains
`8ce89a428d0521344b279a767afaf02051fcdffaeae85ea2f13662745505f919`.

## Offline validation

Completed without a connected bundle command, SQL/job run, Terraform plan,
backend operation, or cloud mutation:

| Gate | Result |
| --- | --- |
| Goal 4 deterministic static validator | PASS |
| Focused Goal 4 regression tests | PASS — 26 tests |
| Full offline pytest suite | PASS — 44 tests |
| Branch coverage | PASS — 96.67%, threshold 90% |
| Ruff format and lint | PASS — 70 files |
| Strict mypy | PASS — 5 source files |
| Bandit | PASS |
| Environment example and infrastructure preflight | PASS |
| Bundle/resource YAML parse | PASS |
| detect-secrets over tracked and untracked candidates | PASS |
| Terraform recursive format and bootstrap/development validate | PASS |
| Terraform mock-provider contracts | PASS — 7 runs, 0 failed |

The first environment-validation invocation omitted the virtual-environment
site-packages path and failed to import `pydantic`. The corrected offline
invocation included both the virtual environment and package source and passed;
this was a command invocation defect, not a configuration failure.

Terraform provider-schema execution required the already-restored provider
binaries outside the filesystem sandbox because the sandbox blocks the plugin
handshake. The successful commands used offline `TF_DATA_DIR` caches and ran no
init, backend, plan, apply, or cloud operation.

TFLint and Trivy were not rerun because their temporary binaries are no longer
present and no IaC source changed in this remediation. Their latest durable
Goal 4 runs remain PASS. `pip-audit` was not rerun because no dependency or lock
file changed.

## Next approval boundary

After offline validation and change-set review, request one strict connected
bundle validation for the exact aggregate source above. Do not deploy, rerun a
negative job, execute Terraform, or mutate AWS under that approval.
