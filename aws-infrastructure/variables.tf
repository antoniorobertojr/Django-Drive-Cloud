variable "region" {
  description = "Aws region to create resources in"
  default     = "us-east-2"
}

variable "project_name" {
  description = "Project name to use in resources names"
  default     = "django-file-manager"
}

variable "availability_zones" {
  description = "Availability zones"
  default     = ["us-east-2a", "us-east-2c"]
}

# ecs

variable "ecs_prod_backend_retention_days" {
  description = "Retention period for backend logs"
  default     = 30
}

# rds

variable "prod_rds_db_name" {
  description = "RDS database name"
  default     = "django_aws"
}
variable "prod_rds_username" {
  description = "RDS database username"
  default     = "django_aws"
}
variable "prod_rds_password" {
  description = "postgres password for production DB"
}
variable "prod_rds_instance_class" {
  description = "RDS instance type"
  default     = "db.t4g.micro"
}

# s3

variable "prod_media_bucket" {
  description = "S3 Bucket for production media files"
  default     = "prod-media-asasdf123df34d1sadfjlk1"
}

