output "prod_lb_domain" {
  value = aws_lb.prod.dns_name
}

output "ecr_repository" {
  value = aws_ecr_repository.backend.repository_url
  description = "The repository URL for the backend ECR repository."
}
