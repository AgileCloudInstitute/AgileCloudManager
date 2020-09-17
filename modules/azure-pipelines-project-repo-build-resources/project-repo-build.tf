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
    working_dir = "/home/agile-cloud/cloned-repos/agile-cloud-manager/pipeline-tasks/"
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
