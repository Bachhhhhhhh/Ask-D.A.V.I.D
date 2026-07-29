output "bucket_names" { value = { for purpose, bucket in aws_s3_bucket.this : purpose => bucket.bucket } }
