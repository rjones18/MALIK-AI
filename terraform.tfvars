# ------------------
# Global
# ------------------
region      = "us-east-1"
environment = "dev"

# ------------------
# Networking (VPC)
# ------------------
vpc_id = "vpc-078e539d3ca103ab4"

public_subnet_ids = [
  "subnet-0014a61f63ea4d2d1",
  "subnet-0e4986877e7c89648"
]

private_subnet_ids = [
  "subnet-0dce3c4bd03d097fa",
  "subnet-099a288adb57e1d67"
]

# ------------------
# ECS / App settings
# ------------------
app_name        = "malik-ai"
container_port = 8080
desired_count  = 2
cpu             = 1024
memory          = 2048

ecr_image = "614768946157.dkr.ecr.us-east-1.amazonaws.com/malik-ai:latest"

# ------------------
# Secrets
# ------------------
secrets_manager_arn = "arn:aws:secretsmanager:us-east-1:614768946157:secret:MALIK_SECRETS-35Qfrv"

# ------------------
# Tags
# ------------------
tags = {
  Project     = "Malik-AI"
  Environment = "dev"
  Owner       = "Reggie"
  ManagedBy   = "Terraform"
}
