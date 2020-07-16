####################################################################################################################
####Define the input variables:  
####################################################################################################################

###The following are for 2nd iteration
variable "subscriptionName" { }  
variable "subscriptionId" { }  
variable "tenantId" { }  
#The client referred to is an App Registration we created for the subscription.  
variable "clientName" { }  
variable "clientId" { }  
variable "clientSecret" { }  
variable "serviceConnectionName" { } 
variable "storageAccountNameTerraformBackend" { }  
variable "storageContainerNameTerraformBackend" { }  
variable "pipeResourceGroupName" { }  
variable "pipeKeyVaultName" { }  
variable "azdoOrgPAT" { }  
variable "azdoOrgServiceURL" { }  
variable "sourceRepo" { }  
variable "projectName" { }  
variable "repoName" { }  
variable "buildName" { }  
#Keeping the next two because we will add secrets definition later.  For now, the secrets have already been entered into the key vault.
variable "awsPublicAccessKey" { }
variable "awsSecretAccessKey" { }

#Use this data source to access the configuration of the azurerm provider, which you configured above:
data "azurerm_client_config" "current" {}

##Define the output variables
#Output the project id for use in script that will wrap this program.
output "azuredevops_project_id" { value = azuredevops_project.project.id }
output "azuredevops_git_repository_id" { value = azuredevops_git_repository.repository.id }
output "azuredevops_git_repository_name" { value = azuredevops_git_repository.repository.name }
output "azuredevops_git_repository_default_branch" { value = azuredevops_git_repository.repository.default_branch }
output "azuredevops_git_repository_is_fork" { value = azuredevops_git_repository.repository.is_fork }
output "azuredevops_git_repository_remote_url" { value = azuredevops_git_repository.repository.remote_url }
output "azuredevops_git_repository_size" { value = azuredevops_git_repository.repository.size }
output "azuredevops_git_repository_ssh_url" { value = azuredevops_git_repository.repository.ssh_url }
output "azuredevops_git_repository_url" { value = azuredevops_git_repository.repository.url }
output "azuredevops_git_repository_web_url" { value = azuredevops_git_repository.repository.web_url }
output "azuredevops_project_name" { value = azuredevops_project.project.project_name }
output "azuredevops_build_definition_id" { value = azuredevops_build_definition.build.id }
output "azuredevops_organization_service_url" { value = var.azdoOrgServiceURL }
output "azuredevops_key_vault_name" { value = var.pipeKeyVaultName }  
output "azuredevops_subscription_name" { value = var.subscriptionName }  
output "azuredevops_subscription_id" { value = var.subscriptionId }  
output "azuredevops_client_name" { value = var.clientName }  
output "azuredevops_service_connection_name" { value = var.serviceConnectionName }  
