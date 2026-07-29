variable "name_prefix" { type = string }
variable "application_subnet_ids" { type = list(string) }
variable "alb_security_group_id" { type = string }
variable "tags" { type = map(string) }
