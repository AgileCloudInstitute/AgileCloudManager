####################################################################################################################
####Define the input variables:  
####################################################################################################################
# variable "subscriptionId" { }  
# variable "tenantId" { }  
# #The client referred to is an App Registration we created for the subscription.  
# variable "clientId" { }  
# variable "clientSecret" { }  
variable "azdoOrgPAT" { }  
variable "azdoOrgServiceURL" { }  
variable "sourceRepo" { }  
variable "projectName" { }  
variable "repoName" { }  
variable "buildName" { }  

data "azuredevops_project" "p" {  project_name = var.projectName  }

output "azuredevops_build_definition_id" { value = azuredevops_build_definition.build.id }
output "azuredevops_git_repository_name" { value = azuredevops_git_repository.repository.name }

#Use this data source to access the configuration of the azurerm provider, which you configured with the input variables above:
#data "azurerm_client_config" "current" {}
