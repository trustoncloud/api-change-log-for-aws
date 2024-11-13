resource "aws_s3_bucket" "website" {
  bucket = var.domain
  acl    = "public-read"
  policy = templatefile("bucket_policy.json", { domain = var.domain })
  tags   = var.resource_tags

  website {
    index_document = "index.html"
    error_document = "error.html"
  }
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

resource "aws_s3_bucket" "access_log" {
  bucket = "${var.app}-${random_string.bucket_suffix.id}"
  tags   = var.resource_tags
}
