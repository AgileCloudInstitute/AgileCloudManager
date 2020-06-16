####################################################################################################################
####Define the input variables:  
####################################################################################################################
#Make sure the subscription is correct, as we are using multiple subscriptions to segregate work

###The following are for 2nd iteration
variable "subscriptionId" { }
variable "tenantId" { }
#The client referred to is an App Registration.  Here, we are using "AppPipes" app registration we create for the second subscription.
variable "clientId" { }
variable "clientSecret" { }
variable "resourceGroupName" { }
variable "resourceGroupLocation" { }
variable "nicName" { }
variable "adminUser" { }
variable "adminPwd" { }
variable "storageAccountDiagName" { }
variable "pathToCloudInitScript" { }

##Manually imported things need placeholders as follows:

data "azurerm_resource_group" "pipeline-resources" {
  name = var.resourceGroupName
}

data "azurerm_network_interface" "myterraformnic" {
  name                = var.nicName
  resource_group_name = var.resourceGroupName
}

data "azurerm_storage_account" "mystorageaccount" {
  name                = var.storageAccountDiagName
  resource_group_name = var.resourceGroupName
}
