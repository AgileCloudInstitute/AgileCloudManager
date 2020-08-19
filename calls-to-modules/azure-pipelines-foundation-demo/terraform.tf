##Backend
terraform {
  backend "s3" {}
}

data "terraform_remote_state" "state" {
  backend = "s3"
  config {
    bucket         = var.s3BucketNameTF
    dynamodb_table = var.dynamoDbTableNameTF
    region         = var.pipeAzureRegion
    key            = var.s3KeyNameTF
  }
}
