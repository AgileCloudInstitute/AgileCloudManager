####################################################################################################################
####Define the input variables:  
####################################################################################################################
variable "subscriptionName" { }  
variable "subscriptionId" { }  
variable "tenantId" { }  
#The client referred to is an App Registration we created for the subscription.  
variable "clientName" { }  
variable "clientId" { }  
variable "clientSecret" { }  
variable "azdoOrgPAT" { }  
variable "azdoOrgServiceURL" { }  
variable "projectName" { }  

#Use this data source to access the configuration of the azurerm provider, which you configured using the above variables:
data "azurerm_client_config" "current" {}

