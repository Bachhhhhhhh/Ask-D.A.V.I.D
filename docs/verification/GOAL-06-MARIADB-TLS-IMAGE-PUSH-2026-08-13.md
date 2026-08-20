# Goal 6 MariaDB TLS remediation image — ECR push evidence

Date: 2026-08-13
AWS account: `736956442295`
AWS region: `ap-southeast-1`
Repository: `ask-david-development/doris-verifier`

## Exact approved artifact

- source aggregate:
  `ab6bc4dceabf86134ac526707b592d1e95137076ecbf55343b12eabfcee5b142`;
- scanned local image ID:
  `sha256:d51145436a95ba7e2b553411e9036362122b14dc201f9ebc8e06b45d852196d6`;
- immutable tag: `goal6-mariadb-ssl-ab6bc4d`.

## Push result

The exact image was pushed to:

`736956442295.dkr.ecr.ap-southeast-1.amazonaws.com/ask-david-development/doris-verifier:goal6-mariadb-ssl-ab6bc4d`

Read-only ECR inspection confirmed:

- digest: `sha256:d51145436a95ba7e2b553411e9036362122b14dc201f9ebc8e06b45d852196d6`;
- tag: `goal6-mariadb-ssl-ab6bc4d`;
- media type: `application/vnd.oci.image.index.v1+json`;
- image size: `17,886,361` bytes.

The Docker login was passed via stdin and logout completed immediately after
inspection. A shell reporting-command quoting error produced a non-zero exit
after Docker had already printed the successful registry digest; no retry or
second push occurred.

No Terraform, ECS task, Databricks, SQL, or other AWS mutation occurred.

## Next approval boundary

The next step is to update the ignored development verifier image input and
create a saved Terraform plan. Apply of task-definition changes and any task
retry require separate approvals.
