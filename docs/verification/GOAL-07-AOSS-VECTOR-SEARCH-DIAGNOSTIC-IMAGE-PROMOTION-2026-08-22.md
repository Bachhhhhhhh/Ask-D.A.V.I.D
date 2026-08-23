# Goal 7 AOSS vector-search diagnostic image promotion — 2026-08-22

## Approved boundary

The offline diagnostic remediation was approved for image build and ECR
promotion. The operation was limited to local image build, private ECR push,
and immediate read-only digest/scan inspection. No Terraform, ECS task,
Databricks, SQL, AOSS data-plane, or other AWS resource operation was run.

## Artifact

| Field | Result |
| --- | --- |
| AWS account / region | `736956442295` / `ap-southeast-1` |
| Source aggregate SHA-256 | `60a6611d2a9f081f0c8fc34a7881db0a7a3e6befd12a9c17a1d80e61ba490f57` |
| Local image digest | `sha256:1be0e8d301f136230795d16bc086a0a90823646f4ca239155924ca13837e5779` |
| Repository | `736956442295.dkr.ecr.ap-southeast-1.amazonaws.com/ask-david-development/langgraph-runtime` |
| Immutable tag | `goal7-indexer-aoss-diagnostics-60a6611d` |
| ECR digest | `sha256:1be0e8d301f136230795d16bc086a0a90823646f4ca239155924ca13837e5779` |
| Entrypoint | `python -m ask_david_goal7.indexer` |
| Image user | `65532:65532` |

## Evidence

- Goal 7 static validation: PASS.
- Goal 7 regression tests: `32 passed`.
- Network-disabled image import: PASS; `_response_shape` is present.
- ECR repository preflight: immutable tags and scan-on-push enabled.
- Push: PASS; ECR digest matches the local image digest.
- ECR scan lookup: `ScanNotFoundException`; scan result is UNVERIFIED and was
  not retried.
- Ignored `terraform.tfvars` was not changed.

## Next approval boundary

The next step is to update only the ignored development indexer image digest,
run offline preflight, and create/review a saved connected Terraform plan. No
task may run until that plan is separately approved and applied.
