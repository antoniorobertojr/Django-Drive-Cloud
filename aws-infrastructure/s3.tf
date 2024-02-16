resource "aws_s3_bucket" "prod_media" {
  bucket = var.prod_media_bucket
}

resource "aws_s3_bucket_cors_configuration" "prod_media" {
  bucket = aws_s3_bucket.prod_media.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

resource "aws_s3_bucket_acl" "prod_media" {
  bucket     = aws_s3_bucket.prod_media.id
  acl        = "private"
  depends_on = [aws_s3_bucket_ownership_controls.s3_bucket_acl_ownership]
}

resource "aws_s3_bucket_ownership_controls" "s3_bucket_acl_ownership" {
  bucket = aws_s3_bucket.prod_media.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
  depends_on = [aws_s3_bucket_public_access_block.prod_media_public_access_block]
}

resource "aws_iam_user" "prod_media_bucket" {
  name = "prod-media-bucket"
}

resource "aws_iam_user_policy" "prod_media_bucket" {
  user = aws_iam_user.prod_media_bucket.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:*",
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:s3:::${var.prod_media_bucket}",
          "arn:aws:s3:::${var.prod_media_bucket}/*"
        ]
      },
    ]
  })
}

resource "aws_iam_access_key" "prod_media_bucket" {
  user = aws_iam_user.prod_media_bucket.name
}

resource "aws_s3_bucket_public_access_block" "prod_media_public_access_block" {
  bucket = aws_s3_bucket.prod_media.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
