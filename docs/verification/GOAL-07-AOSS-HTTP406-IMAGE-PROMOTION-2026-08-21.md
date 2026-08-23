# Goal 7 AOSS HTTP 406 corrected image promotion — 2026-08-21

## Status

**IMAGE BUILT, SCANNED LOCALLY AS AVAILABLE, AND PUSHED — NO TASK RUN**

The corrected source from the AOSS HTTP 406 offline remediation was built
from `docker/Dockerfile.goal7-indexer` and promoted to the existing private
ECR repository. No Terraform or ECS task operation was performed in this
checkpoint.

## Immutable artifact

| Property | Value |
| --- | --- |
| AWS account / region | `736956442295` / `ap-southeast-1` |
| Source aggregate | `16f0bfb0cba5708a521f40de2b52ad0b8fc004d9347d84804646b221a659c260` |
| Local image/index digest | `sha256:56263b9c594825f1509f305bb9911b499acd944dcc9971731d04dc18b530a641` |
| Repository | `736956442295.dkr.ecr.ap-southeast-1.amazonaws.com/ask-david-development/langgraph-runtime` |
| Immutable tag | `goal7-indexer-aoss406-16f0bfb0` |
| Remote digest | `sha256:56263b9c594825f1509f305bb9911b499acd944dcc9971731d04dc18b530a641` |
| Manifest | `application/vnd.oci.image.index.v1+json` |
| Remote scan status | `null` — findings UNVERIFIED |

## Local checks

- Docker build with `--pull=false`: PASS;
- image user: `65532:65532`;
- entrypoint: `python -m ask_david_goal7.indexer`;
- Linux/amd64 image inspection: PASS;
- network-disabled Python import: PASS;
- Trivy: not available in the current local environment.

## Next approval boundary

Update the ignored development image digest, run offline preflight, create a
saved connected Terraform plan, and review that it changes only the Goal 7
indexer task definition. Applying that plan and running a new private task
remain separate approvals. No task retry occurred here.
