# Remote-state bootstrap

The bootstrap root creates an encrypted, versioned, public-blocked state bucket
and KMS key using **local state only**. It must be reviewed and applied only in
Checkpoint 3B with explicit approval for the target development AWS account.
After approval, copy the outputs to the development `backend.hcl`, run
`terraform init -migrate-state`, and retain access only for approved Terraform
principals. State is sensitive: it can contain resource metadata and values
marked sensitive; never commit state files, plan files, or backend credentials.
