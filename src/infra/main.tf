terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  # local backend (no S3 state for local dev)
}

provider "aws" {
  region = var.aws_region
}
