terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.60"
    }
  }
}

locals {
  name = var.name
}

# SG for brokers (inbound from allowed client SGs only)
resource "aws_security_group" "msk" {
  name        = "${local.name}-msk-brokers"
  description = "MSK broker SG"
  vpc_id      = var.vpc_id
  tags        = merge(var.tags, { Name = "${local.name}-msk-brokers" })
}

# Kafka listener ports (TLS / IAM-SASL listeners use dynamic ports controlled by MSK).
# We allow all TCP from client SGs to simplify (MSK manages listener ports).
resource "aws_security_group_rule" "from_clients" {
  type                     = "ingress"
  from_port                = 0
  to_port                  = 65535
  protocol                 = "tcp"
  security_group_id        = aws_security_group.msk.id
  source_security_group_id = length(var.allowed_client_sg_ids) > 0 ? var.allowed_client_sg_ids[0] : null
  count                    = length(var.allowed_client_sg_ids) > 0 ? 1 : 0
}

# If multiple client SGs, add rules for the extras
resource "aws_security_group_rule" "from_clients_extra" {
  for_each                 = toset(slice(var.allowed_client_sg_ids, 1, length(var.allowed_client_sg_ids)))
  type                     = "ingress"
  from_port                = 0
  to_port                  = 65535
  protocol                 = "tcp"
  security_group_id        = aws_security_group.msk.id
  source_security_group_id = each.value
}

# Egress to VPC (NAT/endpoint access for control plane etc.)
resource "aws_security_group_rule" "egress_all" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.msk.id
}

# Optional MSK configuration (applies to provisioned only)
resource "aws_msk_configuration" "this" {
  count           = var.variant == "provisioned" && length(trimspace(var.msk_properties)) > 0 ? 1 : 0
  name            = "${local.name}-config"
  kafka_versions  = ["3.7.0"] # adjust as supported
  server_properties = var.msk_properties
}

# Common logging block helper (locals)
locals {
  logging_info = {
    broker_logs = {
      cloudwatch_logs = var.logs_cloudwatch_log_group != null ? [{
        enabled   = true
        log_group = var.logs_cloudwatch_log_group
      }] : []
      s3 = var.logs_s3_bucket != null ? [{
        enabled = true
        bucket  = var.logs_s3_bucket
        prefix  = var.logs_s3_prefix
      }] : []
      firehose = [] # add if you prefer Firehose
    }
  }
}

# -------------------------
# Provisioned MSK cluster
# -------------------------
resource "aws_msk_cluster" "provisioned" {
  count                  = var.variant == "provisioned" ? 1 : 0
  cluster_name           = local.name
  kafka_version          = "3.7.0"
  number_of_broker_nodes = var.num_broker_nodes

  broker_node_group_info {
    instance_type   = var.broker_instance_type
    client_subnets  = var.subnet_ids
    security_groups = [aws_security_group.msk.id]

    storage_info {
      ebs_storage_info {
        volume_size = var.ebs_volume_size_gb
      }
    }
  }
  }

  dynamic "logging_info" {
    for_each = [1]
    content {
      broker_logs {
        cloudwatch_logs {
          enabled   = var.logs_cloudwatch_log_group != null
          log_group = var.logs_cloudwatch_log_group
        }
        s3 {
          enabled = var.logs_s3_bucket != null
          bucket  = var.logs_s3_bucket
          prefix  = var.logs_s3_prefix
        }
      }
    }
  }

  configuration_info {
    arn   = try(aws_msk_configuration.this[0].arn, null)
    revision = try(aws_msk_configuration.this[0].latest_revision, null)
  }

  tags = var.tags
}

# -------------------------
# Serverless MSK cluster
# -------------------------
resource "aws_msk_serverless_cluster" "serverless" {
  count         = var.variant == "serverless" ? 1 : 0
  cluster_name  = local.name
  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [aws_security_group.msk.id]
  }

  client_authentication {
    sasl {
      iam = true
    }
  }

  # Serverless uses AWS-managed encryption at rest; TLS in transit enforced.
  # Logging (broker logs) currently applies to provisioned; leave none here.

  tags = var.tags
}
