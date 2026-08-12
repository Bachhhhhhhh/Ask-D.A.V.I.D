# Goal 4 storage-credential `PATH_EXISTS` remediation

## Scope and boundary

This report records the one-shot credential validation failure and the
approved offline-only declarative remediation. It is not approval for a
connected Terraform plan/apply, another credential validation, bundle
deployment, SQL execution, or Goal 5 work.

## Applied bootstrap evidence

- Initial IAM role remediation saved-plan SHA-256:
  `2ddc27a4336db94dbb9b159af1b4d2389752e017f0260635c0e5bfa4b6cb0d6d`.
  Result: `2 added, 1 changed, 0 destroyed`.
- Self-assumption trust-policy saved-plan SHA-256:
  `395828d28b26aae401dae740c69f9b20693dae7a5c34d0764278c12c797d5c59`.
  Result: `0 added, 1 changed, 0 destroyed`.
- Post-apply trust inspection retained the Databricks Unity Catalog principal,
  exact external-ID condition, and added only the role self-principal.

## Failed validation evidence

Exactly one approved validation ran for storage credential
`ask-david-development-managed-iceberg` against the approved Raw root in AWS
account `736956442295`, Region `ap-southeast-1`, and Databricks workspace
`7474644358733471`.

The API response reported:

| Operation | Result |
| --- | --- |
| `READ` | PASS |
| `LIST` | PASS |
| `WRITE` | PASS |
| `DELETE` | PASS |
| `PATH_EXISTS` | FAIL |
| Three response entries without an operation label | PASS |

The response also reported `isDir = true` but supplied no failure message.
No retry ran. `DELETE = PASS` is evidence that the validator removed its own
temporary test object; it is not independent proof that no other object exists
under the prefix.

## Root-cause assessment

Repository source declares seven S3 prefixes but no durable object at any
managed root. S3 prefixes are not first-class directories. A zero-byte object
whose key ends in `/` is the documented S3 representation of an empty folder.
Therefore the strongest repository-supported explanation is that the empty
Raw prefix could pass temporary object I/O while failing the separate
`PATH_EXISTS` check after no durable object remained. This remains an inference
until a post-remediation credential validation passes every operation.

## Declarative remediation

Terraform now declares exactly seven zero-byte trailing-slash markers, one for
the catalog root and one for each approved `green_sm_*` schema root. Each
marker:

- derives its bucket and prefix from the verified Goal 3 storage outputs;
- exists only while Goal 4 is `bootstrap` or `active`;
- is explicitly encrypted with the existing storage KMS key;
- contains no data record or Green SM business data;
- does not change the Unity Catalog IAM/KMS permission scope;
- is not an Iceberg table, external table, external volume, or Goal 5 asset.

## Offline verification

Completed on `2026-08-11` without an AWS or Databricks operation:

| Gate | Result |
| --- | --- |
| Terraform format check over `infrastructure/` | PASS |
| Bootstrap Terraform initialization with backend disabled and local provider mirror | PASS |
| Bootstrap `terraform validate` | PASS |
| Development Terraform initialization with backend disabled and local provider mirror | PASS |
| Development `terraform validate` | PASS |
| Development Terraform mock-provider tests | PASS — 7 runs, 0 failed |
| Goal 4 deterministic static validator | PASS |
| Ruff format check | PASS — 63 files |
| Ruff lint | PASS |
| Strict mypy | PASS — 5 source files |
| Pytest | PASS — 28 tests |
| Branch coverage | PASS — 96.67%, threshold 90% |
| Safe environment-example validation | PASS |
| Infrastructure preflight | PASS — structurally valid state KMS ARN |
| Bandit | PASS |
| pip-audit | PASS |
| detect-secrets baseline hook | PASS |
| TFLint | PASS |
| Trivy HIGH/CRITICAL configuration scan | PASS — 0 findings using embedded checks |
| YAML/size/final-newline hygiene | PASS |
| Merge-marker, tracked-sensitive-artifact, and `git diff --check` checks | PASS |

The new Terraform tests prove that the checked-in `disabled` stage declares no
markers and the `bootstrap` stage declares exactly these seven keys:

- `unity-catalog/development/catalog/`;
- `unity-catalog/development/green_sm_raw/`;
- `unity-catalog/development/green_sm_curated/`;
- `unity-catalog/development/green_sm_business/`;
- `unity-catalog/development/green_sm_ai/`;
- `unity-catalog/development/green_sm_platform/`;
- `unity-catalog/development/green_sm_sandbox/`.

Static mutation tests also reject non-empty content, non-KMS encryption,
missing trailing slashes, and marker creation outside the enabled Goal 4
stages.

During validation, one focused pytest invocation executed all 10 Goal 4 static
tests successfully but returned nonzero because the repository-wide coverage
configuration measures only the application package. The authoritative full
suite then passed all 28 tests and its 90% coverage gate. An initial Terraform
mock run exposed that tests inherited ignored local tfvars; fixtures were
corrected to pin stage and self-assumption inputs, after which all 7 Terraform
runs passed. A sandboxed pip-audit attempt could not resolve PyPI; the approved
metadata-only retry completed successfully. Trivy could not refresh its checks
bundle because its container network was deliberately disabled and therefore
used its embedded ruleset, which reported zero HIGH/CRITICAL findings.

Terraform formatting also normalized the ignored local development
`terraform.tfvars`. Terraform formatting is semantic-preserving; no input
value was changed. The file remains ignored and is not part of the change set.

## Next approval boundaries

## Subsequent connected evidence

- The separately reviewed marker plan was applied as exactly seven
  `aws_s3_object` creates, with zero update/replacement/destroy and zero
  Databricks action.
- Read-only object inspection showed all seven markers at zero bytes, encrypted
  with `aws:kms` and the approved storage KMS key.
- The separately approved second storage-credential validation ran exactly
  once. `READ`, `LIST`, `WRITE`, `DELETE`, `PATH_EXISTS`, and the three
  unlabeled response checks all returned `PASS`; the response reported
  `isDir = true`.
- The active-stage saved plan SHA-256
  `c4a81b50ef40531b38a1f785f861d281db02b9e20bc391b209b4c906dafe8502`
  applied as `54 added, 1 changed, 0 destroyed`. It had zero AWS action and no
  replacement, destroy, metastore/assignment, warehouse/cluster, production,
  or Goal 5+ action.
- Immediate read-only inspection verified the storage credential, seven
  external locations, development catalog and six schemas, identities,
  memberships, entitlements, grants, workspace bindings, and service-principal
  access-control rules. The existing Serverless SQL warehouse remained
  stopped, and no project cluster existed.

The marker and active-stage plans are stale after successful apply and must
never be reused. Goal 4 remains unverified until bundle/SQL execution,
authorization, lineage/history, final drift, and durable acceptance evidence
are complete.

## References

- [Databricks storage-credential validation API](https://docs.databricks.com/api/workspace/storagecredentials/validate)
- [Amazon S3 folder markers](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-folders.html)
