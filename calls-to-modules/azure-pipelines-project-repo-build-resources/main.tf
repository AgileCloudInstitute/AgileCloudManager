
module "azure-pipelines-project-repo-build-resources" {
  source = "../../modules/azure-pipelines-project-repo-build-resources"

  subscriptionId                       = "${var.subscriptionId}"
  tenantId                             = "${var.tenantId}"
  clientId                             = "${var.clientId}"
  clientSecret                         = "${var.clientSecret}"
  storageAccountNameTerraformBackend   = "${var.storageAccountNameTerraformBackend}"
  storageContainerNameTerraformBackend = "${var.storageContainerNameTerraformBackend}"
  pipeResourceGroupName                = "${var.pipeResourceGroupName}"
  pipeKeyVaultName                     = "${var.pipeKeyVaultName}"
  azdoOrgPAT                           = "${var.azdoOrgPAT}"
  azdoOrgServiceURL                    = "${var.azdoOrgServiceURL}"
  sourceRepo                           = "${var.sourceRepo}"  
  projectName                          = "${var.projectName}"  
  repoName                             = "${var.repoName}"  
  buildName                            = "${var.buildName}"  
  awsPublicAccessKey                   = "${var.awsPublicAccessKey}"
  awsSecretAccessKey                   = "${var.awsSecretAccessKey}"
}

variable "subscriptionId" { }
variable "tenantId" { }
#The client referred to is an App Registration we created for the subscription.
variable "clientId" { }
variable "clientSecret" { }
variable "storageAccountNameTerraformBackend" { }
variable "storageContainerNameTerraformBackend" { }
variable "pipeResourceGroupName" { }
variable "pipeKeyVaultName" { }
variable "azdoOrgPAT" { }
variable "azdoOrgServiceURL" { }
variable "sourceRepo" { }
variable "projectName" { default = "terraform-simple-pipeline-demo" }
variable "repoName" { default = "terraform-aws-simple-example" }
variable "buildName" { default = "terraform-aws-simple-example" }
variable "awsPublicAccessKey" { }
variable "awsSecretAccessKey" { }
  
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
output "azuredevops_key_vault_name" { value = "${module.azure-pipelines-project-repo-build-resources.azuredevops_key_vault_name}" }  
