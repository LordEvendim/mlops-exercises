terraform {
  required_version = ">=1.7.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    region = "us-east-1"
    bucket = "bartosz-terraform-bucket" 
    key    =  "ecr_repo/terraform.tfstate"
   }
}

provider "aws" {
   region = "us-east-1"
}
