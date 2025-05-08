variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "polars-benchmark"
}

variable "bucket_name_prefix" {
  description = "Prefix for the S3 bucket name"
  type        = string
  default     = "pds"
}

variable "ecr_repository_name" {
  description = "Name of the ECR repository"
  type        = string
  default     = "polars-benchmark"
}

variable "container_image_tag" {
  description = "Tag for the container image"
  type        = string
  default     = "latest"
} 