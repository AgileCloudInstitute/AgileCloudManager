
module "azure-pipelines-foundation-demo" {
  source = "../../modules/azure-pipelines-foundation"

  subscriptionId                       = "${var.subscriptionId}"
  tenantId                             = "${var.tenantId}"
  clientId                             = "${var.clientId}"
  clientSecret                         = "${var.clientSecret}"
  pipeAzureRegion                      = "${var.pipeAzureRegion}"

}

##Input variables.  The client referred to is an App Registration.
variable "subscriptionId" { }
variable "tenantId" { }
variable "clientId" { }
variable "clientSecret" { }
variable "pipeAzureRegion" { }

  
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
