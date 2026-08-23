# Goal 7 AOSS search content-type image promotion — 2026-08-21

## Status

**PUSHED — NO TASK RUN**

The image built from the content-type remediation was pushed to the existing
private ECR repository. No Terraform operation, ECS task, Databricks operation,
or AOSS data-plane mutation occurred in this checkpoint.

## Immutable artifact

| Attribute | Value |
| --- | --- |
| AWS account / region | `736956442295` / `ap-southeast-1` |
| Source aggregate | `32d8209e72ff5a5c7b2113bd810880c7a9602a8c82a633de32ba0b585f038cc1` |
| Repository | `736956442295.dkr.ecr.ap-southeast-1.amazonaws.com/ask-david-development/langgraph-runtime` |
| Immutable tag | `goal7-indexer-aoss-content-32d8209e` |
| Local image digest | `sha256:7f1072ca1e969932a95c9fd53d97201a57cd25521f23d8663f5460af5b1b6586` |
| Remote image digest | `sha256:7f1072ca1e969932a95c9fd53d97201a57cd25521f23d8663f5460af5b1b6586` |
| Manifest | `application/vnd.oci.image.index.v1+json` |
| Remote image size | `43,259,417` bytes |
| Local/remote digest match | PASS |
| ECR scan inspection | UNVERIFIED — `ScanNotFoundException`; no retry |

The repository was revalidated as immutable with scan-on-push enabled before
promotion. Docker's local credential-helper warning was not a credential
value; no credential was read, printed, or committed.

## Next checkpoint

Goal 7 remains **UNVERIFIED**. The next separately approved boundary is to
update only the ignored development indexer image digest, run offline
preflight, and create a saved connected Terraform plan whose only expected
managed action is replacement of the Goal 7 indexer task definition.
