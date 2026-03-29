variable "aws_region" {
  description = "AWS region where all resources will be deployed."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name prefix applied to every resource."
  type        = string
  default     = "emotion-detector"
}

variable "image_tag" {
  description = "Docker image tag to pull from ECR and deploy."
  type        = string
  default     = "latest"
}

variable "acm_certificate_arn" {
  description = "ACM certificate ARN for HTTPS on the ALB. Leave empty to keep HTTP only."
  type        = string
  default     = ""
}

variable "enable_managed_https" {
  description = "If true, Terraform requests an ACM certificate, validates it in Route 53 and configures HTTPS on the ALB."
  type        = bool
  default     = false
}

variable "route53_zone_id" {
  description = "Public Route 53 hosted zone ID used for ACM DNS validation and ALB alias record."
  type        = string
  default     = ""
}

variable "route53_zone_name" {
  description = "Public Route 53 hosted zone name used for ACM DNS validation and ALB alias record."
  type        = string
  default     = ""
}

variable "custom_domain_name" {
  description = "Fully qualified domain name for the app. If empty, project_name.route53_zone_name will be used."
  type        = string
  default     = ""
}

# ─ ECS Fargate Specific ─────────────────────────────────────────────────────

variable "ecs_task_cpu" {
  description = "CPU units for ECS task (256, 512, 1024, 2048, 4096)."
  type        = string
  default     = "1024"
}

variable "ecs_task_memory" {
  description = "Memory (MB) for ECS task (512, 1024, 2048, 4096, 8192, etc)."
  type        = string
  default     = "2048"
}

variable "ecs_desired_count" {
  description = "Desired number of ECS tasks (load balanced)."
  type        = number
  default     = 2
}

variable "ecs_max_count" {
  description = "Maximum number of ECS tasks for auto-scaling."
  type        = number
  default     = 4
}

