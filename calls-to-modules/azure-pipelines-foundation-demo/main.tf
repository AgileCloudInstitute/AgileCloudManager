
module "azure-pipelines-foundation-demo" {
  source = "../../modules/azure-pipelines-foundation"

  subscriptionId     = "${var.subscriptionId}"
  tenantId           = "${var.tenantId}"
  clientId           = "${var.clientId}"
  clientSecret       = "${var.clientSecret}"
  pipeAzureRegion    = "${var.pipeAzureRegion}"
  awsPublicAccessKey = "${var.awsPublicAccessKey}"
  awsSecretAccessKey = "${var.awsPublicAccessKey}"
}

##Input variables.  The client referred to is an App Registration.
variable "subscriptionId" { }
variable "tenantId" { }
variable "clientId" { }
variable "clientSecret" { }
variable "pipeAzureRegion" { }
variable "awsPublicAccessKey" { }
variable "awsSecretAccessKey" { }

##Output variables
output "pipes_resource_group_name" { value = "${module.azure-pipelines-foundation-demo.pipes_resource_group_name}" }
output "pipes_resource_group_region" { value = "${module.azure-pipelines-foundation-demo.pipes_resource_group_region}" }
output "pipes_subnet_id" { value = "${module.azure-pipelines-foundation-demo.pipes_subnet_id}" }
output "nicName" { value = "${module.azure-pipelines-foundation-demo.nicName}" }
output "storageAccountDiagName" { value = "${module.azure-pipelines-foundation-demo.storageAccountDiagName}" }
output "pipeKeyVaultName" { value = "${module.azure-pipelines-foundation-demo.pipeKeyVaultName}" }
output "currentConfig" { value = "${module.azure-pipelines-foundation-demo.currentConfig}" }

output "subscription_name" { value = "${module.azure-pipelines-foundation-demo.subscription_name}" }
output "subscription_id" { value = "${module.azure-pipelines-foundation-demo.subscription_id}" }
output "tenant_id" { value = "${module.azure-pipelines-foundation-demo.tenant_id}" }

output "admin_ip_body" { value = "${module.azure-pipelines-foundation-demo.admin_ip_body}" }
output "admin_cider" { value = "${module.azure-pipelines-foundation-demo.admin_cider}" }

  
