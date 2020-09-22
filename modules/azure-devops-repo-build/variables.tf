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

data "azuredevops_project" "p" {  project_identifier = var.projectName  }

#Use this data source to access the configuration of the azurerm provider, which you configured with the input variables above:
#data "azurerm_client_config" "current" {}
