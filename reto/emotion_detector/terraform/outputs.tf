output "ecr_repository_url" {
  description = "ECR repository URL (use this to tag and push your image)."
  value       = aws_ecr_repository.app.repository_url
}

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer."
  value       = aws_lb.app.dns_name
}

output "custom_domain_name" {
  description = "Custom DNS name assigned to the application when managed HTTPS is enabled."
  value       = local.use_managed_https ? local.app_domain_name : null
}

output "app_url" {
  description = "Complete URL to access the Emotion Detector application."
  value       = local.use_https ? "https://${local.public_hostname}" : "http://${local.public_hostname}"
}

output "https_enabled" {
  description = "Whether HTTPS is enabled on the ALB."
  value       = local.use_https
}

output "certificate_arn" {
  description = "ACM certificate ARN in use for the ALB HTTPS listener."
  value       = local.use_https ? local.effective_certificate_arn : null
}

output "push_commands" {
  description = "Commands to build and push the Docker image to ECR."
  value       = <<-EOT
    # Run these from the project root (where the Dockerfile lives):

    # 1. Authenticate Docker to ECR
    aws ecr get-login-password --region ${var.aws_region} | \
      docker login --username AWS --password-stdin ${aws_ecr_repository.app.repository_url}

    # 2. Build
    docker build -t ${var.project_name} .

    # 3. Tag
    docker tag ${var.project_name}:latest ${aws_ecr_repository.app.repository_url}:${var.image_tag}

    # 4. Push
    docker push ${aws_ecr_repository.app.repository_url}:${var.image_tag}

    # 5. Update ECS service (pulls new image)
    aws ecs update-service --cluster ${aws_ecs_cluster.app.name} --service ${aws_ecs_service.app.name} --force-new-deployment
  EOT
}

output "cloudwatch_logs" {
  description = "CloudWatch Log Group for ECS container logs."
  value       = "Log group: ${aws_cloudwatch_log_group.app.name}"
}

