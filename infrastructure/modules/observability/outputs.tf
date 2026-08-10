output "alert_topic_arn" { value = aws_sns_topic.alerts.arn }
output "rds_cpu_alarm_name" { value = aws_cloudwatch_metric_alarm.rds_cpu_high.alarm_name }
output "runtime_log_group_arn" { value = aws_cloudwatch_log_group.runtime.arn }
