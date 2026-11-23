output "rds_host" {
  description = "RDS instance hostname"
  value       = aws_db_instance.postgres.address
}

output "rds_port" {
  description = "RDS instance port"
  value       = aws_db_instance.postgres.port
}

output "rds_endpoint" {
  description = "RDS instance endpoint (host:port)"
  value       = aws_db_instance.postgres.endpoint
}

output "database_url" {
  # The AWS emulator provides RDS API emulation only — it does not expose a
  # real PostgreSQL wire endpoint. Actual connections use the postgres:16
  # sidecar container on 127.0.0.1:5433 (managed by manage.sh emulator:start).
  description = "Connection URL for the main database (postgres sidecar)"
  value       = "postgresql+psycopg2://${var.db_username}:${var.db_password}@127.0.0.1:5433/${var.db_name}"
  sensitive   = true
}

output "test_database_url" {
  description = "Connection URL for the test database (postgres sidecar)"
  value       = "postgresql+psycopg2://${var.db_username}:${var.db_password}@127.0.0.1:5433/${var.db_name}_test"
  sensitive   = true
}

output "ecr_repository_url" {
  description = "ECR repository URL for the API image"
  value       = aws_ecr_repository.api.repository_url
}

output "alb_dns_name" {
  description = "ALB DNS name"
  value       = aws_lb.main.dns_name
}

output "api_url" {
  description = "Base URL for the API"
  value       = "http://${aws_lb.main.dns_name}"
}
