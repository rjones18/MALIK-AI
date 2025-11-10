variable "name" {
  description = "Base name for the MSK cluster."
  type        = string
}

variable "variant" {
  description = "msk variant: provisioned or serverless"
  type        = string
  validation {
    condition     = contains(["provisioned", "serverless"], var.variant)
    error_message = "variant must be one of: provisioned, serverless."
  }
}

variable "vpc_id" {
  description = "VPC ID where MSK runs."
  type        = string
}

variable "subnet_ids" {
  description = "Private subnet IDs (recommend 3 across AZs)."
  type        = list(string)
}

variable "allowed_client_sg_ids" {
  description = "Security Group IDs allowed to reach brokers."
  type        = list(string)
  default     = []
}

variable "kms_key_arn" {
  description = "KMS key for at-rest encryption. If null, AWS managed key is used."
  type        = string
  default     = null
}

# --- Provisioned-only knobs ---
variable "broker_instance_type" {
  description = "Broker instance type (provisioned only)."
  type        = string
  default     = "kafka.m7g.large"
}

variable "num_broker_nodes" {
  description = "Total number of brokers (provisioned only; use multiples of AZs)."
  type        = number
  default     = 3
}

variable "ebs_volume_size_gb" {
  description = "EBS volume size per broker in GB (provisioned only)."
  type        = number
  default     = 1000
}

variable "msk_properties" {
  description = <<DESC
Kafka server.properties content for an aws_msk_configuration (optional).
If empty, configuration is not attached.
DESC
  type        = string
  default     = ""
}

variable "logs_s3_bucket" {
  description = "If set, broker logs go to this S3 bucket prefix."
  type        = string
  default     = null
}
variable "logs_s3_prefix" {
  description = "S3 log prefix."
  type        = string
  default     = "msk-logs/"
}

variable "logs_cloudwatch_log_group" {
  description = "If set, broker logs go to this CloudWatch Log Group."
  type        = string
  default     = null
}

variable "tags" {
  description = "Common tags."
  type        = map(string)
  default     = {}
}
