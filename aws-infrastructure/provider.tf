provider "aws" {
  region = var.region
}
terraform {
  backend "s3" {
    bucket = "terraform-django-file-manager-backend"
    key    = "terraform"
    region = "us-east-2"
  }
}
