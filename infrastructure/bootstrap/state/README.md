# Remote-state bootstrap

The bootstrap root creates an encrypted, versioned, public-blocked state bucket
and KMS key using **local state only**. It must be reviewed and applied only in
Checkpoint 3B with explicit approval for the target development AWS account.

Before that approval, initialize and plan/apply this root with local state;
it deliberately has no backend declaration. After the approved bootstrap apply:

1. Read the non-secret `state_bucket_name` and `state_kms_key_arn` outputs.
2. Copy `backend.tf.example` to the ignored `backend.tf` in this directory.
3. Copy `backend.hcl.example` to the ignored `backend.hcl` in this directory,
   use `bootstrap/terraform.tfstate` as its key, and insert those outputs.
4. Migrate the bootstrap local state with `terraform init -migrate-state
   -backend-config=backend.hcl`.
5. Put the same bucket, region, and KMS ARN in the development backend while
   using the distinct key `development/terraform.tfstate`.

Retain access only for approved Terraform principals. State is sensitive: it
can contain resource metadata and values marked sensitive; never commit state
files, plan files, or backend credentials.

The KMS key policy captures the caller identity that performs the approved
bootstrap apply. It permits that identity to manage the key and use it only
through S3 for the state bucket. A later operator identity requires a reviewed
Terraform policy change before it can access state.
