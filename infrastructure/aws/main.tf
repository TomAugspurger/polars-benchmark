terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
  required_version = ">= 1.0"
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project = "polars-benchmark"
      owner = "toaugspurger"
      team = "rapidsai"
    }
  }
}

provider "random" {}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

module "s3" {
  source = "./modules/s3"
  
  bucket_name_prefix = var.bucket_name_prefix
  bucket_name_suffix = random_string.bucket_suffix.result
}
