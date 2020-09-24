module "azure-devops-project" {
  source = "../../../modules/azure-devops-project"

  subscriptionName                     = "${var.subscriptionName}"  
  subscriptionId                       = "${var.subscriptionId}"  
  tenantId                             = "${var.tenantId}"  
  clientName                           = "${var.clientName}"  
  clientId                             = "${var.clientId}"  
  clientSecret                         = "${var.clientSecret}"  
  azdoOrgPAT                           = "${var.azdoOrgPAT}"  
  azdoOrgServiceURL                    = "${var.azdoOrgServiceURL}"  
  projectName                          = "${var.projectName}"  
}

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

output "azuredevops_service_connection_id" { value = "${module.azure-devops-project.azuredevops_service_connection_id}" }
output "azuredevops_project_id" { value = "${module.azure-devops-project.azuredevops_project_id}" }
