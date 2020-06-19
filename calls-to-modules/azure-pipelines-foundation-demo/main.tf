
module "azure-pipelines-foundation-demo" {
  source = "../../modules/azure-pipelines-foundation"

  subscriptionId                     = "${var.subscriptionId}"
  tenantId                           = "${var.tenantId}"
  clientId                           = "${var.clientId}"
  clientSecret                       = "${var.clientSecret}"
  storageAccountNameTerraformBackend = "${var.storageAccountNameTerraformBackend}"
  pipeAzureRegion                    = "${var.pipeAzureRegion}"
}

##Input variables
variable "subscriptionId" { }
variable "tenantId" { }
#The client referred to is an App Registration.
variable "clientId" { }
variable "clientSecret" { }
variable "storageAccountNameTerraformBackend" { }
variable "pipeAzureRegion" { }

##Output variables
output "pipes_resource_group_name" { value = "${module.azure-pipelines-foundation-demo.pipes_resource_group_name}" }
output "pipes_resource_group_region" { value = "${module.azure-pipelines-foundation-demo.pipes_resource_group_region}" }
output "pipes_storage_account_name" { value = "${module.azure-pipelines-foundation-demo.pipes_storage_account_name}" }
output "nicName" { value = "${module.azure-pipelines-foundation-demo.nicName}" }
output "storageAccountDiagName" { value = "${module.azure-pipelines-foundation-demo.storageAccountDiagName}" }
output "pipeKeyVaultName" { value = "${module.azure-pipelines-foundation-demo.pipeKeyVaultName}" }
output "currentConfig" { value = "${module.azure-pipelines-foundation-demo.currentConfig}" }
