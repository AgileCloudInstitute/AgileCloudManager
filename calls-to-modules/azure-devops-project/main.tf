module "azure-pipelines-project-repo-build-resources" {
  source = "../../modules/azure-pipelines-project-repo-build-resources"

  subscriptionName                     = "${var.subscriptionName}"  
  subscriptionId                       = "${var.subscriptionId}"  
  tenantId                             = "${var.tenantId}"  
  clientName                           = "${var.clientName}"  
  clientId                             = "${var.clientId}"  
  clientSecret                         = "${var.clientSecret}"  
  serviceConnectionName                = "${var.serviceConnectionName}"  
  subnetId                             = "${var.subnetId}"
  resourceGroupLocation                = "${var.resourceGroupLocation}"
  resourceGroupName                    = "${var.resourceGroupName}"  
  azdoOrgPAT                           = "${var.azdoOrgPAT}"  
  azdoOrgServiceURL                    = "${var.azdoOrgServiceURL}"  
  sourceRepo                           = "${var.sourceRepo}"  
  projectName                          = "${var.projectName}"  
  repoName                             = "${var.repoName}"  
  buildName                            = "${var.buildName}"  
}

variable "subscriptionName" { }  
variable "subscriptionId" { }  
variable "tenantId" { }  
#The client referred to is an App Registration we created for the subscription.
variable "clientName" { }
variable "clientId" { }
variable "clientSecret" { }
variable "serviceConnectionName" { }
variable "subnetId" { }
variable "resourceGroupLocation" { }
variable "resourceGroupName" { }
variable "azdoOrgPAT" { }
variable "azdoOrgServiceURL" { }
variable "sourceRepo" { }
variable "projectName" { }
variable "repoName" { }
variable "buildName" { }

##Output variables  
output "azuredevops_project_id" { value = "${module.azure-pipelines-project-repo-build-resources.azuredevops_project_id}" }  
output "azuredevops_git_repository_id" { value = "${module.azure-pipelines-project-repo-build-resources.azuredevops_git_repository_id}" }  
output "azuredevops_git_repository_name" { value = "${module.azure-pipelines-project-repo-build-resources.azuredevops_git_repository_name}" }  
output "azuredevops_git_repository_default_branch" { value = "${module.azure-pipelines-project-repo-build-resources.azuredevops_git_repository_default_branch}" }  
output "azuredevops_git_repository_is_fork" { value = "${module.azure-pipelines-project-repo-build-resources.azuredevops_git_repository_is_fork}" }  
output "azuredevops_git_repository_remote_url" { value = "${module.azure-pipelines-project-repo-build-resources.azuredevops_git_repository_remote_url}" }  
output "azuredevops_git_repository_size" { value = "${module.azure-pipelines-project-repo-build-resources.azuredevops_git_repository_size}" }  
output "azuredevops_git_repository_ssh_url" { value = "${module.azure-pipelines-project-repo-build-resources.azuredevops_git_repository_ssh_url}" }  
output "azuredevops_git_repository_url" { value = "${module.azure-pipelines-project-repo-build-resources.azuredevops_git_repository_url}" }  
output "azuredevops_git_repository_web_url" { value = "${module.azure-pipelines-project-repo-build-resources.azuredevops_git_repository_web_url}" }  
output "azuredevops_project_name" { value = "${module.azure-pipelines-project-repo-build-resources.azuredevops_project_name}" }  
output "azuredevops_build_definition_id" { value = "${module.azure-pipelines-project-repo-build-resources.azuredevops_build_definition_id}" }  
output "azuredevops_organization_service_url" { value = "${module.azure-pipelines-project-repo-build-resources.azuredevops_organization_service_url}" }  
output "azuredevops_subscription_name" { value = "${module.azure-pipelines-project-repo-build-resources.azuredevops_subscription_name}" }  
output "azuredevops_subscription_id" { value = "${module.azure-pipelines-project-repo-build-resources.azuredevops_subscription_id}" }  
output "azuredevops_client_name" { value = "${module.azure-pipelines-project-repo-build-resources.azuredevops_client_name}" }  
output "azuredevops_service_connection_name" { value = "${module.azure-pipelines-project-repo-build-resources.azuredevops_service_connection_name}" }  
output "azuredevops_service_connection_id" { value = "${module.azure-pipelines-project-repo-build-resources.azuredevops_service_connection_id}" }  