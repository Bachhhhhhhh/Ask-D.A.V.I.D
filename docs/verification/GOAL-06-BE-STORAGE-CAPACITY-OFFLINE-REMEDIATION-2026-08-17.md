# Goal 6 BE storage-capacity offline remediation

Date: 2026-08-17
Environment: development only
Status: **SUPERSEDED BY USER-DATA-SIZE REMEDIATION — CONNECTED PLAN/APPLY NOT AUTHORIZED**

## Triggering evidence

The separately approved single revision-8 admin-refresh task
`e7f51fa2d2994c8289b7c7ac00d035b6` stopped with exit code `1`. After explicit
approval, the one non-secret Doris error event was retrieved. It reports that
the only registered BE (`10.42.71.97`) has empty HDD and SSD disk maps, so FE
cannot place even the requested one replica.

The internal serving DDL already sets `"replication_num" = "1"`; reducing
replication is neither necessary nor an acceptable workaround. This result
does not test Unity Catalog, OAuth, S3, KMS, or the source lakehouse table.

## Declarative correction

The Terraform-rendered BE bootstrap now:

1. creates the exact EBS-backed `be-storage` bind source before Docker can
   create it implicitly;
2. configures `storage_root_path` as
   `/opt/apache-doris/be/storage,medium:hdd`;
3. verifies the mounted root from the Doris image's configured container user,
   rather than accepting host-root writability;
4. uses a bounded private `SHOW BACKENDS` check after the BE listener opens;
5. accepts BE capacity only if the matching host is alive, not decommissioned,
   and reports non-zero total capacity; and
6. emits non-secret terminal markers
   `be-storage-root-unavailable` or `be-storage-capacity-unavailable` on
   failure, or `be-storage-root-writable` then `be-storage-capacity-ready` on
   success.

This does not create an external storage path, alter S3/Unity Catalog,
weaken a security group, change a Doris replica count, or delete/create a
data volume. Because the shared rendered host bootstrap changes, a future
Terraform plan may propose FE/BE instance replacement to rerun cloud-init;
that plan must be reviewed before any apply. The current encrypted data
volumes must remain attached/reused exactly as the plan proves.

## Validation required and run

| Check | Result |
| --- | --- |
| `bash -n infrastructure/modules/doris-serving/templates/doris-host.sh.tftpl` | PASS |
| `python3 scripts/validate_goal6.py` | PASS |
| `pytest -q -p no:cacheprovider -o addopts='' tests/unit/test_goal6_static.py` | PASS |
| `python3 -m compileall -q scripts/validate_goal6.py` | PASS |
| `terraform fmt -check -recursive infrastructure` | PASS |
| `terraform -chdir=infrastructure/environments/development init -backend=false -input=false` | PASS — temporary `TF_DATA_DIR`; no backend configured |
| `terraform -chdir=infrastructure/environments/development validate` | PASS — temporary `TF_DATA_DIR` |
| `terraform -chdir=infrastructure/modules/doris-serving test -test-directory=tests` | PASS — 1 passed, 0 failed; temporary `TF_DATA_DIR` |
| `git diff --check` | PASS |

Ruff, mypy, TFLint, and Trivy are not installed locally, so their checks are
**UNVERIFIED** rather than inferred. AWS inspection, Terraform connected plan/
apply, ECR, ECS task execution, and Databricks operations were not run by this
remediation.

## Superseding offline blocker

The first subsequent saved-plan attempt stopped before it could create an
artifact because AWS provider validation rejected the rendered EC2 `user_data`
payload as larger than its 16,384-byte limit. No apply, ECS task, or other AWS
mutation occurred. The storage-capacity correction itself remains intact, but
its connected-plan checkpoint is superseded by
[`GOAL-06-EC2-USER-DATA-LENGTH-OFFLINE-REMEDIATION-2026-08-17.md`](GOAL-06-EC2-USER-DATA-LENGTH-OFFLINE-REMEDIATION-2026-08-17.md).

## Historical next approval boundary

Re-run the available offline validation suite, then obtain approval for a
saved connected development Terraform plan. The plan must be reviewed for:

- no EBS volume create/update/replace/destroy;
- no public exposure, IAM/KMS/S3/Databricks change, or production action;
- only the reviewed host bootstrap replacements/attachment reattachments, if
  Terraform requires them; and
- no ECS task execution.
