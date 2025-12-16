resource "random_id" "bucket_suffix" {
  count       = length(var.regions)
  keepers = {
    force_regenerate = timestamp()
  }
  byte_length = 6
}

module "s3_us_east_1" {
  source              = "./modules/s3_bucket"
  bucket_name_prefix  = var.bucket_name_prefix
  region              = var.regions[0]
  random_suffix       = random_id.bucket_suffix[0].hex
}

module "s3_us_west_2" {
  source              = "./modules/s3_bucket"
  providers = {
    aws = aws.us_west_2
  }
  bucket_name_prefix  = var.bucket_name_prefix
  region              = var.regions[1]
  random_suffix       = random_id.bucket_suffix[1].hex
  lifecycle_days      = 30
}
