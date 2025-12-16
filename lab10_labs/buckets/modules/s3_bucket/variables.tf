variable "bucket_name_prefix" {
  type        = string
  description = "S3 bucket prefix"
}

variable "region" {
  type        = string
  description = "AWS region"
}

variable "random_suffix" {
  type        = string
  description = "Random suffix"
}

variable "lifecycle_days" {
  type        = number
  default     = 90
  description = "Days before objects transition"
}

variable "lifecycle_storage_class" {
  type        = string
  default     = "GLACIER"
  description = "Storage class"
}