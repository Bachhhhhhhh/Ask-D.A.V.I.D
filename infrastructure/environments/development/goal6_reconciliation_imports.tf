// These imports reconcile only resources created by the approved Goal 6
// foundation apply but missing from remote Terraform state after the partial
// apply. They do not create, replace, or destroy AWS resources.

import {
  for_each = var.goal_6_enabled ? toset(["fe-instance"]) : toset([])

  to = module.doris_serving.aws_instance.fe[0]
  id = "i-074e456efa350b444"
}

import {
  for_each = var.goal_6_enabled ? toset(["fe-attachment"]) : toset([])

  to = module.doris_serving.aws_volume_attachment.fe[0]
  id = "/dev/sdf:vol-012bc3410278ed85e:i-074e456efa350b444"
}

import {
  for_each = var.goal_6_enabled ? toset(["be-attachment"]) : toset([])

  to = module.doris_serving.aws_volume_attachment.be[0]
  id = "/dev/sdf:vol-01e9b0ed05f7b92b9:i-05b409f7992294844"
}
