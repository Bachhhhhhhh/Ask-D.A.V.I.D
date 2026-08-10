[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$ExpectedAccountId,
    [Parameter(Mandatory = $true)][string]$Region,
    [Parameter(Mandatory = $true)][string]$RdsIdentifier,
    [Parameter(Mandatory = $true)][string]$RdsCpuAlarmName,
    [Parameter(Mandatory = $true)][double]$RdsCpuAlarmThresholdPercent,
    [Parameter(Mandatory = $true)][string]$AlertTopicArn,
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

$alarmResult = (& aws cloudwatch describe-alarms --region $Region --alarm-names $RdsCpuAlarmName --query 'MetricAlarms[0]' --output json)
if ($LASTEXITCODE -ne 0) {
    throw "The base RDS CPU alarm could not be inspected."
}
$alarm = $alarmResult | ConvertFrom-Json
if ($null -eq $alarm) {
    throw "The base RDS CPU alarm was not returned."
}
$dimensions = @($alarm.Dimensions)
$alarmActions = @($alarm.AlarmActions)
$okActions = @($alarm.OKActions)
$insufficientDataActions = @($alarm.InsufficientDataActions)

if (
    $alarm.AlarmName -ne $RdsCpuAlarmName -or
    $alarm.Namespace -ne "AWS/RDS" -or
    $alarm.MetricName -ne "CPUUtilization" -or
    $alarm.Statistic -ne "Average" -or
    $alarm.Unit -ne "Percent" -or
    $alarm.ComparisonOperator -ne "GreaterThanThreshold" -or
    $alarm.Period -ne 60 -or
    $alarm.EvaluationPeriods -ne 5 -or
    $alarm.DatapointsToAlarm -ne 5 -or
    [double]$alarm.Threshold -ne $RdsCpuAlarmThresholdPercent -or
    $alarm.TreatMissingData -ne "missing" -or
    -not $alarm.ActionsEnabled -or
    $dimensions.Count -ne 1 -or
    $dimensions[0].Name -ne "DBInstanceIdentifier" -or
    $dimensions[0].Value -ne $RdsIdentifier -or
    $alarmActions.Count -ne 1 -or
    $alarmActions[0] -ne $AlertTopicArn -or
    $okActions.Count -ne 0 -or
    $insufficientDataActions.Count -ne 0
) {
    throw "The base RDS CPU alarm does not match the approved read-only contract."
}

Write-Output "Read-only base RDS CPU alarm contract verification passed."
Write-Output "Read-only smoke-test discovery completed. Validate expected private endpoints and SG paths against Terraform outputs."
