[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$ExpectedAccountId,
    [Parameter(Mandatory = $true)][string]$Region,
    [Parameter(Mandatory = $true)][string]$RdsIdentifier,
    [Parameter(Mandatory = $true)][string]$RedisReplicationGroupId,
    [switch]$ConfirmCheckpoint3B
)

if (-not $ConfirmCheckpoint3B) {
    throw "Checkpoint 3B approval is required. This script performs read-only AWS describe calls only."
}

$account = aws sts get-caller-identity --query Account --output text
if ($account -ne $ExpectedAccountId) { throw "AWS account mismatch; no tests were run." }
aws rds describe-db-instances --region $Region --db-instance-identifier $RdsIdentifier --query 'DBInstances[0].PubliclyAccessible'
aws elasticache describe-replication-groups --region $Region --replication-group-id $RedisReplicationGroupId
Write-Output "Read-only smoke-test discovery completed. Validate expected private endpoints and SG paths against Terraform outputs."
