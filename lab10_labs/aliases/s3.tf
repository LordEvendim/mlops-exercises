resource "aws_s3_bucket" "my_bucket" {
  bucket = "my-bucket-afdab234423"
  tags = {
    Name = "my-bucket"
  }
}

resource "aws_s3_bucket" "my_bucket_us_west_2" {
  bucket   = "my-bucket-afdab23442432432"
  provider = aws.us_west_2
  tags = {
    Name = "my-bucket"
  }
}