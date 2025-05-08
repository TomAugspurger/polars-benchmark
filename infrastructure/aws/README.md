# AWS Infrastructure for Polars Benchmark Runner

This directory contains Terraform/OpenTofu configuration to deploy the Polars Benchmark container to AWS.

## Resources Created

1. **S3 Bucket**: Stores benchmark data with a randomly generated unique name (`pds-{random-string}`)
2. **ECR Repository**: Hosts the Docker container image
3. **ECS Cluster, Task Definition and scheduled event**: Runs the benchmark container as a scheduled task

## Prerequisites

- AWS CLI installed and configured with appropriate credentials
- Terraform (v1.0+) or OpenTofu installed

## Usage

1. Initialize the Terraform/OpenTofu configuration:

```bash
tofu init
```

2. Review the planned changes:

```bash
tofu plan
```

3. Apply the configuration:

```bash
tofu apply
```

4. After successful apply, note the outputs:
   - S3 bucket name
   - ECR repository URL
   - ECS cluster name
   - CloudWatch log group

5. Build and push the Docker image to the ECR repository:

```bash
# Log in to ECR
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com

# Build the image
docker build -t <ecr-repo-url>:latest ../..

# Push the image
docker push <ecr-repo-url>:latest
```

6. The ECS task is scheduled to run daily using CloudWatch Events. You can also run it manually using the AWS CLI or console.

## Cleanup

To remove all created resources:

```bash
terraform destroy
# or
tofu destroy
```