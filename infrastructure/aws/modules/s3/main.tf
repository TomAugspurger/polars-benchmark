resource "aws_s3_bucket" "benchmark_bucket" {
  bucket = "${var.bucket_name_prefix}-${var.bucket_name_suffix}"

  lifecycle {
    prevent_destroy = false
  }
}

resource "aws_s3_bucket_public_access_block" "benchmark_bucket" {
  bucket = aws_s3_bucket.benchmark_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "benchmark_bucket" {
  bucket = aws_s3_bucket.benchmark_bucket.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
} 