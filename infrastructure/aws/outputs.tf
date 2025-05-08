output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = module.s3.bucket_name
}

# output "ecr_repository_url" {
#   description = "URL of the ECR repository"
#   value       = module.ecr.repository_url
# }

# output "ecs_cluster_name" {
#   description = "Name of the ECS cluster"
#   value       = module.ecs.cluster_arn
# }

# output "task_definition_arn" {
#   description = "ARN of the ECS task definition"
#   value       = module.ecs.task_definition_arn
# }

# output "cloudwatch_log_group" {
#   description = "Name of the CloudWatch log group"
#   value       = module.ecs.cloudwatch_log_group
# } 