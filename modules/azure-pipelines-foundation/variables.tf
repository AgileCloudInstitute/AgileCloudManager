###############################################################################################
##First section here is from the general foundation NOT including AD stuff
####################################################################################################################
####Define the input variables:  
####################################################################################################################
#Make sure the subscription is correct, as we are using multiple subscriptions to segregate work

###The following are for 2nd iteration
variable "subscriptionId" { }
variable "tenantId" { }
#The client referred to is an App Registration.  MAKE A FINAL DECISION ABOUT WHAT THIS WILL BE HERE AND DOCUMENT IT IN VISIO.
variable "clientId" { }
variable "clientSecret" { }
variable "pipeAzureRegion" { }

# Workstation External IP. Override with variable or hardcoded value if necessary.
data "http" "admin-external-ip" { url = "http://ipv4.icanhazip.com" }
locals { admin-external-cidr = "${chomp(data.http.admin-external-ip.body)}/32" }

##Define the output variables
output "pipes_resource_group_name" { value = azurerm_resource_group.pipelines.name }
output "pipes_resource_group_region" { value = azurerm_resource_group.pipelines.location }
output "pipes_subnet_id" { value = azurerm_subnet.pipelines.id }
output "nicName" { value = azurerm_network_interface.myterraformnic.name }
output "storageAccountDiagName" { value = azurerm_storage_account.mystorageaccount.name }
output "pipeKeyVaultName" { value = azurerm_key_vault.infraPipes.name }
output "currentConfig" { value = data.azurerm_client_config.current }

data "azurerm_subscription" "current" {}
output "subscription_name" { value = data.azurerm_subscription.current.display_name }
output "subscription_id" { value = data.azurerm_subscription.current.subscription_id }
output "tenant_id" { value = data.azurerm_subscription.current.tenant_id }
