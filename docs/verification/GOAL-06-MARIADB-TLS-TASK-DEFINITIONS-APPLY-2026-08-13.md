# Goal 6 MariaDB TLS task-definition apply evidence

Date: 2026-08-13
AWS account: `736956442295`
AWS region: `ap-southeast-1`
Saved plan SHA-256: `7f4de065ecae0de13d97954bc97314306af7a09b50831c2cf85048ea00b39aa0`

## Apply result

The exact approved saved plan was applied without creating an implicit plan:

`Apply complete! Resources: 2 added, 0 changed, 2 destroyed.`

The expected ECS task-definition revision replacements were the only managed
resource actions. No ECS task was launched.

## Read-only post-apply inspection

Both active revision-3 task definitions were inspected:

| Family | Revision | Image | Mode |
| --- | ---: | --- | --- |
| `ask-david-development-doris-admin-refresh` | 3 | approved digest `sha256:d51145436a95ba7e2b553411e9036362122b14dc201f9ebc8e06b45d852196d6` | Fargate / `awsvpc` |
| `ask-david-development-doris-verifier` | 3 | approved digest `sha256:d51145436a95ba7e2b553411e9036362122b14dc201f9ebc8e06b45d852196d6` | Fargate / `awsvpc` |

The admin command is `/app/doris-admin-refresh`; the verifier command is
`/app/doris-readonly-verify`. ECS reported zero running tasks after apply.

The next checkpoint is a separately approved single private admin-refresh task
using revision 3. If it fails, stop without retry.
