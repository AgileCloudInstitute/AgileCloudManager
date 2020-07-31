#The Azure DevOps resources, including a project, a repository, and a build.

resource "azuredevops_project" "project" {
  project_name       = var.projectName
  visibility         = "private"
  version_control    = "Git"
  work_item_template = "Agile"
}

resource "azuredevops_git_repository" "repository" {
  project_id = azuredevops_project.project.id
  name = var.repoName
  initialization {
    init_type = "Uninitialized"
  }
  provisioner "local-exec" {
    command = "az repos import create --git-source-url \"${var.sourceRepo}\" --repository \"${azuredevops_git_repository.repository.name}\" --organization \"${var.azdoOrgServiceURL}\" --project \"${azuredevops_project.project.project_name}\""
    working_dir = "/home/aci-user/cloned-repos/agile-cloud-manager/pipeline-tasks/"
  }
}

resource "azuredevops_build_definition" "build" {
  project_id = azuredevops_project.project.id
  name       = var.buildName
  ci_trigger {
    use_yaml = true
  }

  repository {
    repo_type   = "TfsGit"
    repo_id     = azuredevops_git_repository.repository.id
    #repo_name     = azuredevops_git_repository.repository.id
    #branch_name = azuredevops_git_repository.repository.default_branch
    yml_path    = "azure-pipelines.yml"
  }
}

resource "azuredevops_serviceendpoint_azurerm" "endpointazure" {  
  project_id            = azuredevops_project.project.id  
  service_endpoint_name = var.clientName  
  description = "Managed by Terraform" 
  credentials {  
    serviceprincipalid  = var.clientId  
    serviceprincipalkey = var.clientSecret  
  }  
  azurerm_spn_tenantid      = var.tenantId  
  azurerm_subscription_id   = var.subscriptionId  
  azurerm_subscription_name = var.subscriptionName  
}  

#The following version is what the documentation calls "automated".  We are commenting this out because we want to pass in one that already has permissions as above.
#resource "azuredevops_serviceendpoint_azurerm" "endpointazure" {
#  project_id                = azuredevops_project.project.id
#  service_endpoint_name     = var.clientName 
#  description = "Managed by Terraform" 
#  azurerm_spn_tenantid      = var.tenantId  
#  azurerm_subscription_id   = var.subscriptionId  
#  azurerm_subscription_name = var.subscriptionName
#}
