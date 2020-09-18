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
#variable "serviceConnectionName" { } 
variable "azdoOrgPAT" { }  
variable "azdoOrgServiceURL" { }  
variable "projectName" { }  

#Use this data source to access the configuration of the azurerm provider, which you configured using the above variables:
data "azurerm_client_config" "current" {}

##Define the output variables
output "azuredevops_project_id" { value = azuredevops_project.project.id }
output "azuredevops_project_name" { value = azuredevops_project.project.project_name }
output "azuredevops_organization_service_url" { value = var.azdoOrgServiceURL }
output "azuredevops_subscription_name" { value = var.subscriptionName }  
output "azuredevops_subscription_id" { value = var.subscriptionId }  
output "azuredevops_client_name" { value = var.clientName }  
#output "azuredevops_service_connection_name" { value = var.serviceConnectionName }  

output "azuredevops_service_connection_id" { value = azuredevops_serviceendpoint_azurerm.endpointazure.id }
